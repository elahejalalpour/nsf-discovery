from resource_broker import ResourceBroker
from container_driver import ContainerDriver
from provisioning_agent import ProvisioningAgent
from ovs_driver import OVSDriver
from veth_driver import VethDriver
from chain_driver import ChainDriver
from discovery_agent import DiscoveryAgent
import time
import threading
import zmq
import platform
import psutil
import fcntl
import struct
import socket
import thread
import json
import argparse


def initialize_resources(resource_broker):
    resource_broker.register_resource("BashWrapper", "bash_wrapper")
    resource_broker.register_resource("ContainerDriver",
                                      ContainerDriver, backing_driver="docker")
    resource_broker.register_resource("VethDriver", VethDriver)
    resource_broker.register_resource("OVSDriver", OVSDriver, resource_broker)
    resource_broker.register_resource("ChainDriver",
                                      ChainDriver, resource_broker)


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,  # SIOCGIFADDR
                                        struct.pack('256s', ifname[:15]))[20:24])


class MinionDaemon(object):

    """
    Creates the minion daemon. Then upon calling the repeat method, the minion
    daemon will periodically pull the message queue for any incoming message
    from the master and take appropriate action based on the received message.
    The daemon also discovers the local VNFs and chain lins and exports this
    data to the master.

    @param resource_broker A ResourceBroker object that is used to provide the
        daemon with the necessary drivers.
    @param sleep_interval The sleep timer interval for the minion daemon.
    @param master_ip IP address of the master node.
    @param master_subs_port Subscriber listening port number for the master.
    @param master_sync_port PULL socket port number for the master.
    @param minion_ip IP address of the minion.
    @param minion_hostname Hostname of the minion.
    @param provisioning_agent A ProvisioningAgent object that is used to
        provision VNFs and the links in between them.
    @param discovery_agent A DiscoveryAgent object that is used to discover the
        VNFs and the links in between them.
    """

    def __init__(self,
                 resource_broker,
                 sleep_interval,
                 master_ip,
                 master_subs_port,
                 master_sync_port,
                 minion_ip,
                 minion_hostname,
                 provisioning_agent,
                 discovery_agent):
        self._resource_broker = resource_broker
        self._sleeping = sleep_interval
        self._container_driver =\
            self._resource_broker.get_resource("ContainerDriver")
        self._ovs_driver = self._resource_broker.get_resource("OVSDriver")
        self._master_ip = master_ip
        self._master_subs_port = master_subs_port
        self._master_sync_port = master_sync_port
        self._default_ovs_bridge = default_ovs_bridge
        self._default_tunnel_interface = default_tunnel_interface
        self._ip_address = minion_ip
        self._minion_hostname = minion_hostname
        self._provisioning_agent = provisioning_agent
        self._discovery_agent = discovery_agent
        self._context, self._subscriber, self._syncclient =\
            self.__init_zeromq()
        self._vnfs = {}

    def __init_zeromq(self):
        context = zmq.Context()
        subscriber = context.socket(zmq.SUB)
        syncclient = context.socket(zmq.PUSH)
        return context, subscriber, syncclient

    def __connect_to_master(self):
        subscriber_con_str = "tcp://" + \
            str(self._master_ip) + ":" + str(self._master_subs_port)
        syncclient_con_str = "tcp://" + \
            str(self._master_ip) + ":" + str(self._master_sync_port)
        self._subscriber.connect(subscriber_con_str)
        self._subscriber.setsockopt(zmq.SUBSCRIBE, '')
        self._syncclient.connect(syncclient_con_str)

    def __register_with_master(self):
        """
        Register minion with master
        """
        msg = {'flag': 'REG', 'host': self._minion_hostname,
               'host_ip': self._ip_address,
               'cpus': len(psutil.cpu_percent(interval=None, percpu=True))}
        # send a synchronization request
        self._syncclient.send_json(msg)

    def command_handler(self, msg):
        try:
            print msg
            if msg['host'] == self._minion_hostname or msg['host'] == '*':
                action = msg['action']
                print("!!!!!!!!!!!!!")
                if action == 'create_chain':
                    self._provisioning_agent.provision_local_chain(msg['data'])
                elif action == 'deploy':
                    ret = self._container_driver.deploy(
                        msg['user'], msg['image_name'], msg['vnf_name'])
                elif action == 'report':
                    self._vnfs = {}
                    return

                container_list = []
                if msg['ID'] == '*':
                    container_list = [
                        c['Id'].encode() for c in self._container_driver.get_containers(full=True)]
                else:
                    container_list.append(msg['ID'])
                for container in container_list:
                    if action == 'start':
                        self._container_driver.start(container)
                    elif action == 'stop':
                        self._container_driver.stop(container)
                    elif action == 'restart':
                        self._container_driver.restart(container)
                    elif action == 'pause':
                        self._container_driver.pause(container)
                    elif action == 'unpause':
                        self._container_driver.unpause(container)
                    elif action == 'destroy':
                        reply = {'host': self._minion_hostname,
                                 'ID': container}
                        if container in self._vnfs:
                            self._container_driver.destroy(
                                container, force=True)
                            del self._vnfs[container]
                            reply['flag'] = 'removed'
                        else:
                            reply['flag'] = 'not_exists'
                        self._syncclient.send_json(reply)
                    elif (msg['action'] == 'execute'):
                        response = self._container_driver.execute_in_guest(
                            msg['ID'], msg['cmd'])
                        reply = {'host': self._minion_hostname, 'ID': msg['ID'],
                                 'flag': 'reply', 'response': response,
                                 'cmd': msg['cmd']}
                        self._syncclient.send_json(reply)
        except Exception as ex:
            print ex
            traceback.print_exc()

    def pull(self):
        try:
            # exhaust the msg queue
            while(True):
                msg = self._subscriber.recv_json(flags=zmq.NOBLOCK)
                self.command_handler(msg)
        except Exception as ex:
            return

    def repeat(self):
        """
        The main loop of the daemon.
        A scheduler repeat exec collect() every interval
        amount of time
        """
        self.__connect_to_master()
        self.__register_with_master()
        while (True):
            self.pull()
            self.collect()
            # time.sleep(interval)
        # threading.Timer(interval, repeat).start()

    def collect(self):
        """
        Collect information from the local machine (container, host info etc.),
        and report it back to the master.
        """
        partial_view = self._discovery_agent.discover()
        containers = self._container_driver.get_containers(full=True)
        for c in containers:
            ID = c['Id'].encode()
            status = self._container_driver.guest_status(ID)
            image = c['Image']
            name = c['Names'][0][1:].encode('ascii')
            # read net_ifs info from partial_view read from discovery module.
            current_container = [container for container in
                                 partial_view['containers'] if
                                 container['container_id'] == name]
            net_ifs = [] if not current_container else\
                current_container[0]['net_ifs']
            msg = {'host': self._minion_hostname, 'ID': ID, 'image': image,
                   'name': name, 'status': status, 'net_ifs': net_ifs}
            if status == 'running':
                msg['IP'] = self._container_driver.get_ip(ID)

            # Only push update for a VNF if it's status has changed, i.e., the
            # container went from running to paused or paused to running etc.
            if ID in self._vnfs:
                if self._vnfs[ID] != status:
                    self._vnfs[ID] = status
                    msg['flag'] = 'update'
            else:
                self._vnfs[ID] = status
                msg['flag'] = 'new'
            if 'flag' in msg:
                self._syncclient.send_json(msg)
                print(msg)
        # push system resource info
        mem = psutil.virtual_memory()
        vnf_images = self._container_driver.images()
        msg = {'host': self._minion_hostname, 'flag': 'sysinfo',
               'cpu': psutil.cpu_percent(interval=float(self._sleeping)),
               'mem_total': mem[0], 'mem_available': mem[1],
               'used': mem[3], 'host_ip': self._ip_address,
               'cpus': psutil.cpu_percent(interval=None, percpu=True),
               'network': psutil.net_io_counters(pernic=True),
               'images': vnf_images}
        self._syncclient.send_json(msg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", help="IP address of the master",
                        default="127.0.0.1")
    parser.add_argument("--master_subs_port", help="ZeroMQ subscriber\
                        number at the master", default="5561")
    parser.add_argument("--master_sync_port", help="ZeroMQ push socket\
                        port number at master", default="5562")
    parser.add_argument("--interface", help="Communication interface of\
                        minion, e.g., eth0", default="eth0")
    parser.add_argument("--default_ovs_bridge", help="Name of the default ovs\
                        bridge", default="ovs-br0")
    parser.add_argument("--default_tunnel_interface", help="Name of the \
                        tunnel interface", default="gre0")
    args = parser.parse_args()
    minion_ip = get_ip_address(args.interface)
    minion_hostname = platform.node()
    default_ovs_bridge = args.default_ovs_bridge
    default_tunnel_interface = args.default_tunnel_interface
    resource_broker = ResourceBroker()
    initialize_resources(resource_broker)
    provisioning_agent = ProvisioningAgent(
        resource_broker,
        default_ovs_bridge,
        default_tunnel_interface)
    discovery_agent = DiscoveryAgent(
        resource_broker,
        default_ovs_bridge)
    ovs_driver = resource_broker.get_resource("OVSDriver")
    if not ovs_driver.is_bridge_created(default_ovs_bridge):
        ovs_driver.create_bridge(default_ovs_bridge)
    ovs_driver.set_bridge_of_version(default_ovs_bridge, "OpenFlow13")
    ovs_driver.set_bridge_fail_mode(default_ovs_bridge, "secure")
    minion_daemon = MinionDaemon(resource_broker, 1.0,
                                 args.master,
                                 args.master_subs_port,
                                 args.master_sync_port,
                                 minion_ip, minion_hostname,
                                 provisioning_agent, discovery_agent)
    minion_daemon.repeat()
