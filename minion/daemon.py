from container_driver import ContainerDriver
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

sleeping = 1.5
mon = ContainerDriver()
dict = {}
# set up zeromq
master = '10.0.1.100'
interface = 'eth0'
context = zmq.Context()
subscriber = context.socket(zmq.SUB)
syncclient = context.socket(zmq.REQ)
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
    # wait for synchronization reply
    syncclient.recv()
    #print('register finished')


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
        syncclient.recv()
    elif (msg['action'] == 'deploy'):
        ret = mon.deploy(msg['user'], msg['image_name'], msg['vnf_name'])
    elif (msg['action'] == 'execute'):
        response = mon.execute_in_guest(msg['ID'], msg['cmd'])
        reply = {'host': hostname, 'ID': msg['ID'],
                 'flag': 'reply', 'response': response, 'cmd': msg['cmd']}
        syncclient.send_json(reply)
        syncclient.recv()
    elif (msg['action'] == 'create_chain'):
        # To be finished
        print("Request received to deploy chain: \n")
        print(msg)
        print("\n")


def cmd_handler(msg):
    """
            handle commands received from master
    """
    try:
        if (hostname == msg['host'] or msg['host'] == '*'):
            # print(msg)
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
            thread.start_new_thread(cmd_handler, (msg,))
    except Exception, ex:
        #print("No New Msg!")
        return


def collect():
    """
            Collect various information of all containers
            on the server
"""
    pull()
    containers = mon.get_containers()
    it = iter(containers)
    for a in it:
        ID = a['Id'].encode()
        status = mon.guest_status(ID)
        image = a['Image']
        name = a['Names'][0]
        # read json chain info from home
        # chain_data = open("/home/nfuser/chain.json").read()
        chain_data = '{"net_ifs":[]}'
        chain_data = json.loads(chain_data)
        # push vnf status info
        if dict.has_key(ID):
            if dict[ID] != status:
                # vnf is in the record but status changed
                msg = {'host': hostname, 'ID': ID, 'image': image,
                       'name': name, 'status': status, 'flag': 'update',
                       'net_ifs': chain_data['net_ifs']}
                if status == 'running':
                    msg['IP'] = mon.get_ip(ID)
                syncclient.send_json(msg)
                syncclient.recv()
                dict[ID] = status
        else:
            # vnf is not in the record,create a new entry
            dict[ID] = status
            msg = {'host': hostname, 'ID': ID, 'image': image,
                   'name': name, 'status': status, 'flag': 'new',
                   'net_ifs': chain_data['net_ifs']}
            if status == 'running':
                msg['IP'] = mon.get_ip(ID)
            syncclient.send_json(msg)
            syncclient.recv()
    # push system resource info
    mem = psutil.virtual_memory()
    images = mon.images()
    msg = {'host': hostname, 'flag': 'sysinfo',
           'cpu': psutil.cpu_percent(interval=sleeping),
           'mem_total': mem[0], 'mem_available': mem[1],
           'used': mem[3], 'host_ip': get_ip_address(interface),
           'cpus': psutil.cpu_percent(interval=None, percpu=True),
           'network': psutil.net_io_counters(pernic=True),
           'images': images}
    syncclient.send_json(msg)
    syncclient.recv()


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
    #threading.Timer(interval, repeat).start()


def main():
    repeat()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", help="IP of the master")
    parser.add_argument("--interface", help="interface of minion")
    args = parser.parse_args()
    if (args.master is not None):
        master = args.master
    if (args.interface is not None):
        interface = args.interface
    subscriber.connect('tcp://' + master + ':5561')
    subscriber.setsockopt(zmq.SUBSCRIBE, '')
    syncclient.connect('tcp://' + master + ':5562')
    main()
