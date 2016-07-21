from container_driver import ContainerDriver
from provisioning_agent import ProvisioningAgent
from ovs_driver import OVSDriver
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

sleeping = 1
mon = ContainerDriver()
dict = {}
# set up zeromq
master = '10.0.1.100'
interface = 'eth0'
default_ovs_bridge = 'ovs-br0'
default_tunnel_interface = 'gre0'
context = zmq.Context()
subscriber = context.socket(zmq.SUB)
syncclient = context.socket(zmq.PUSH)
hostname = platform.node()


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,  # SIOCGIFADDR
                                        struct.pack('256s', ifname[:15]))[20:24])


def register():
    """
            Register minion with master
    """
    msg = {'flag': 'REG', 'host': hostname,
           'host_ip': get_ip_address(interface),
           'cpus': len(psutil.cpu_percent(interval=None, percpu=True))}
    # send a synchronization request
    syncclient.send_json(msg)
    # print('register finished')


def cmd_helper(msg):
    """
            call cooresponding API to execute commands
    """
    if (msg['action'] == 'start'):
        mon.start(msg['ID'])
    elif (msg['action'] == 'stop'):
        mon.stop(msg['ID'])
    elif (msg['action'] == 'restart'):
        mon.restart(msg['ID'])
    elif (msg['action'] == 'pause'):
        mon.pause(msg['ID'])
    elif (msg['action'] == 'unpause'):
        mon.unpause(msg['ID'])
    elif (msg['action'] == 'destroy'):
        mon.stop(msg['ID'])
        mon.destroy(msg['ID'])
        del dict[msg['ID']]
        reply = {'host': hostname, 'ID': msg['ID'],
                 'flag': 'removed'}
        syncclient.send_json(reply)
    elif (msg['action'] == 'deploy'):
        ret = mon.deploy(msg['user'], msg['image_name'], msg['vnf_name'])
    elif (msg['action'] == 'execute'):
        response = mon.execute_in_guest(msg['ID'], msg['cmd'])
        reply = {'host': hostname, 'ID': msg['ID'],
                 'flag': 'reply', 'response': response, 'cmd': msg['cmd']}
        syncclient.send_json(reply)
    elif (msg['action'] == 'create_chain'):
        # To be finished
        print "Request received to deploy chain: \n"
        pa = ProvisioningAgent(ovs_bridge_name=default_ovs_bridge,
                tunnel_interface_name=default_tunnel_interface)
        pa.provision_local_chain(msg['data'])
        # print msg['data']
        # print(json.dumps(msg))
        print("\n")


def cmd_handler(msg):
    """
            handle commands received from master
    """
    try:
        if (hostname == msg['host'] or msg['host'] == '*'):
            print(msg)
            if (msg['action'] == 'create_chain'):
                cmd_helper(msg)
                return
            if (msg['ID'] == '*'):
                containers = mon.get_containers()
                it = iter(containers)
                for a in it:
                    msg['ID'] = a['Id'].encode()
                    cmd_helper(msg)
            else:
                cmd_helper(msg)
    except Exception, ex:
        print(ex)
        pass


def pull():
    """
            check any new message from master
    """
    try:
        # exhaust the msg queue
        while(True):
            msg = subscriber.recv_json(flags=zmq.NOBLOCK)
            cmd_handler(msg)
            # thread.start_new_thread(cmd_handler, (msg,))
    except Exception, ex:
        # print("No New Msg!")
        return


def collect():
    """
        Collect various information of all containers
        on the server
    """
    pull()

    discovery_agent = DiscoveryAgent()
    partial_view = discovery_agent.discover()
    
    containers = mon.get_containers()
    it = iter(containers)
    for a in it:
        ID = a['Id'].encode()
        status = mon.guest_status(ID)
        image = a['Image']
        name = a['Names'][0][1:].encode('ascii');
        # read json chain info from home
        # chain_data = open("/home/nfuser/chain.json").read()
    
        # read net_ifs info from partial_view read from discovery module
        current_container = None
        for container in partial_view['containers']:
            if container['container_id'] == name:
                current_container = container
                break
        print current_container
        if current_container is not None:
            net_ifs = current_container['net_ifs']
        else:
            continue
        # push vnf status info
        if dict.has_key(ID):
            if dict[ID] != status:
                # vnf is in the record but status changed
                msg = {'host' : hostname, 'ID' : ID, 'image' : image,
                        'name' : name, 'status' : status, 'flag' : 'update',
                        'net_ifs' : net_ifs}
                if status == 'running':
                    msg['IP'] = mon.get_ip(ID)
                syncclient.send_json(msg)
                print "VNF status changed:"
                print msg
                dict[ID] = status
        else:
            # vnf is not in the record,create a new entry
            dict[ID] = status
            msg = {'host' : hostname, 'ID' : ID, 'image' : image,
                        'name' : name, 'status' : status, 'flag' : 'new',
                        'net_ifs' : net_ifs}
            if status == 'running':
                msg['IP'] = mon.get_ip(ID)
            print "New VNF entry"
            print msg
            syncclient.send_json(msg)
    # push system resource info
    mem = psutil.virtual_memory()
    images = mon.images()
    msg = {'host' : hostname, 'flag' : 'sysinfo', 
            'cpu' : psutil.cpu_percent(interval=sleeping),
            'mem_total' : mem[0], 'mem_available' : mem[1], 
            'used' : mem[3],'host_ip' : get_ip_address(interface),
            'cpus' : psutil.cpu_percent(interval=None, percpu=True),
            'network' : psutil.net_io_counters(pernic=True),
            'images' : images}
    syncclient.send_json(msg)
        
        
def repeat():
    """
            A scheduler repeat exec collect() every interval
            amount of time
    """
    print(master)
    register()
    while (True):
        collect()
        # time.sleep(interval)
    # threading.Timer(interval, repeat).start()


def main():
    repeat()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", help = "IP address of the master", 
                        default = "127.0.0.1")
    parser.add_argument("--interface", help = "Communication interface of\
                        minion, e.g., eth0", default = "eth0")
    parser.add_argument("--default_ovs_bridge", help = "Name of the default ovs\
                        bridge", default = "ovs-br0")
    parser.add_argument("--default_tunnel_interface", help = "Name of the \
                        tunnel interface", default = "gre0")
    args = parser.parse_args()
    master = args.master
    interface = args.interface
    default_ovs_bridge = args.default_ovs_bridge
    default_tunnel_interface = args.default_tunnel_interface
    OVSDriver.set_bridge_of_version(default_ovs_bridge, "OpenFlow13")
    OVSDriver.set_bridge_fail_mode(default_ovs_bridge, "secure")
    subscriber.connect('tcp://' + master + ':5561')
    subscriber.setsockopt(zmq.SUBSCRIBE, '')
    syncclient.connect('tcp://' + master + ':5562')
    main()
