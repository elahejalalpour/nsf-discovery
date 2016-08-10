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
    resource_broker.register_resource("ContainerDriver",
                                      ContainerDriver, backing_driver="docker")
    resource_broker.register_resource("OVSDriver", OVSDriver)
    resource_broker.register_resource("VethDriver", VethDriver)
    resource_broker.register_resource("ChainDriver",
                                      ChainDriver, resource_broker)

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,  # SIOCGIFADDR
                                        struct.pack('256s', ifname[:15]))[20:24])


class MinionDaemon(object):

    def __init__(self, resource_broker, master_ip, interface="eth0",
                 default_ovs_bridge="ovs0", default_tunnel_interface="gre0"):
        self._resource_broker = resource_broker
        self._sleeping = 1
        self._container_driver =\
            self._resource_broker.get_resource("ContainerDriver")
        self._ovs_driver = self._resource_broker.get_resource("OVSDriver")
        self._master_ip = master_ip
        self._default_ovs_bridge = default_ovs_bridge
        self._default_tunnel_interface = default_tunnel_interface
        self._ip_address = get_ip_address(interface)
        self._hostname = platform.node()
        self._provisioning_agent = ProvisioningAgent(
            resource_broker,
            self._default_ovs_bridge,
            self._default_tunnel_interface)
        self._discovery_agent = DiscoveryAgent(
            self._resource_broker,
            self._default_ovs_bridge)
        self._subscriber = None
        self._syncclient = None
        self._context = None
        self._init_zeromq()

    def _init_zeromq(self):
        self._context = zmq.Context()
        self._subscriber = self._context.socket(zmq.SUB)
        self._syncclient = self._context.socket(zmq.PUSH)

    def connect_to_master(self):
        self._subscriber.connect('tcp://' + master + ':5561')
        self._subscriber.setsockopt(zmq.SUBSCRIBE, '')
        self._syncclient.connect('tcp://' + master + ':5562')

    def register_with_master(self):
        """
        Register minion with master
        """
        msg = {'flag': 'REG', 'host': self._hostname,
               'host_ip': self._ip_address,
               'cpus': len(psutil.cpu_percent(interval=None, percpu=True))}
        # send a synchronization request
        self._syncclient.send_json(msg)

    def command_handler(self, msg):
        try:
            if msg['host'] == self._hostname or msg['host'] == '*':
                action = msg['action']
                if action == 'create_chain':
                    self._provisioning_agent.provision_local_chain(msg['data'])
                elif action == 'deploy':
                    ret = self._container_driver.deploy(
                        msg['user'], msg['image_name'], msg['vnf_name'])

                container_list = []
                if msg['ID'] == '*':
                    container_list = [
                        c['Id'].encode() for c in self._container_driver.get_containers()]
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
                        self._container_driver.stop(container)
                        self._container_driver.destroy(container)
                        # del dict[msg['ID']]
                        reply = {'host': self._hostname, 'ID': msg['ID'],
                                 'flag': 'removed'}
                        self._syncclient.send_json(reply)
                    elif (msg['action'] == 'execute'):
                        response = self._container_driver.execute_in_guest(
                            msg['ID'], msg['cmd'])
                        reply = {'host': self._hostname, 'ID': msg['ID'],
                                 'flag': 'reply', 'response': response,
                                 'cmd': msg['cmd']}
                        self._syncclient.send_json(reply)
        except Exception as ex:
            print ex

    def pull(self):
        try:
            # exhaust the msg queue
            while(True):
                msg = self._subscriber.recv_json(flags=zmq.NOBLOCK)
                self._command_handler(msg)
                # thread.start_new_thread(cmd_handler, (msg,))
        except Exception as ex:
            return

    def repeat(self):
        """
        The main loop of the daemon.
                A scheduler repeat exec collect() every interval
                amount of time
        """
        self.register_with_master()
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
        containers = self._container_driver.get_containers()
        it = iter(containers)
        for a in it:
            ID = a['Id'].encode()
            status = self._container_driver.guest_status(ID)
            image = a['Image']
            name = a['Names'][0][1:].encode('ascii')
            # read net_ifs info from partial_view read from discovery module
            current_container = None
            for container in partial_view['containers']:
                if container['container_id'] == name:
                    current_container = container
                    break
            if current_container is not None:
                net_ifs = current_container['net_ifs']
            else:
                continue
            # push vnf status info
            msg = {'host': self._hostname, 'ID': ID, 'image': image,
                   'name': name, 'status': status, 'flag': 'new',
                   'net_ifs': net_ifs}
            if status == 'running':
                msg['IP'] = self._container_driver.get_ip(ID)

            self._syncclient.send_json(msg)
        # push system resource info
        mem = psutil.virtual_memory()
        images = self._container_driver.images()
        msg = {'host': self._hostname, 'flag': 'sysinfo',
               'cpu': psutil.cpu_percent(interval=self._sleeping),
               'mem_total': mem[0], 'mem_available': mem[1],
               'used': mem[3], 'host_ip': get_ip_address(interface),
               'cpus': psutil.cpu_percent(interval=None, percpu=True),
               'network': psutil.net_io_counters(pernic=True),
               'images': images}
        self._syncclient.send_json(msg)

if __name__ == '__main__':
    global mon
    mon = ContainerDriver(backing_driver = "docker")
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", help="IP address of the master",
                        default="127.0.0.1")
    parser.add_argument("--interface", help="Communication interface of\
                        minion, e.g., eth0", default="eth0")
    parser.add_argument("--default_ovs_bridge", help="Name of the default ovs\
                        bridge", default="ovs-br0")
    parser.add_argument("--default_tunnel_interface", help="Name of the \
                        tunnel interface", default="gre0")
    args = parser.parse_args()
    master = args.master
    interface = args.interface
    default_ovs_bridge = args.default_ovs_bridge
    default_tunnel_interface = args.default_tunnel_interface
    resource_broker = ResourceBroker()
    initialize_resources(resource_broker)
    ovs_driver = resource_broker.get_resource("OVSDriver")
    ovs_driver.set_bridge_of_version(default_ovs_bridge, "OpenFlow13")
    ovs_driver.set_bridge_fail_mode(default_ovs_bridge, "secure")
    minion_daemon = MinionDaemon(resource_broker, master, interface,
                                 default_ovs_bridge, default_tunnel_interface)
    minion_daemon.connect_to_master()
    minion_daemon.repeat()
