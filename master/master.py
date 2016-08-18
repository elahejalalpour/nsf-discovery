# Master
from __future__ import division
import copy
import zmq
import time
import json
import etcd
import traceback
import dateutil.parser
from datetime import datetime
import ipaddress
import networkx as nx
from networkx.readwrite import json_graph
from copy import deepcopy
import argparse
import logger
import uuid
import host_manager
import chain_manager


class MasterMonitor():

    def __init__(self, sleeping, etcdcli, influx, publisher, syncservice, ipc, interval, hostmanager, chainmanager):
        self._sleeping = sleeping
        self._etcdcli = etcdcli
        self._influx = influx
        self._publisher = publisher
        self._syncservice = syncservice
        self._ipc = ipc
        self._interval = interval
        self._hostmanager = hostmanager
        self._chainmanager = chainmanager


    def msg_handler(self, msg):
        """
            handles messages recv from minions
        """
        # print(msg)
        try:
            if (msg['flag'] == 'REG'):
                # A new Host joined in the management network
                print('New Host Registered: ' + msg['host'])
                self._hostmanager.host_register(msg)

            elif(msg['flag'] == 'sysinfo'):
                # A Host pushed system resource info
                self._hostmanager.update_host(msg)

            elif(msg['flag'] == 'new' or msg['flag'] == 'update'):
                # A new VNF is detected or a status change in existing VNF
                self._chainmanager.update_vnf(msg)
                if (msg['status'] == 'running'):
                    self._chainmanager.construct_chain()
            else:
                # print(msg)
                pass
        except Exception as ex:
            print(ex)
            traceback.print_exc()

    def ipc_handler(self, msg):
        """
            handles messages from IPC(typically commands)
        """
        mssg = copy.deepcopy(msg)
        if mssg['action'] == 'create_chain':
            k = 0
            print mssg
            self._chainmanager.create_chain(mssg)
        else:
            print mssg
            self._publisher.send_json(mssg)
            try:
                if (msg['action'] == 'destroy'):
                    r = self._etcdcli.read('/VNF', recursive=True, sorted=True)
                    for child in r.children:
                        temp = json.loads(child.value)
                        if (temp['Host_name'] == msg['host'] and
                                temp['Con_id'] == msg['ID']):
                            self._etcdcli.delete(child.key)
            except Exception as ex:
                print(ex)
                traceback.print_exc()


    def start(self):
        '''
            master starts to wrok
        '''
        while(True):
            try:
                # exhaust the msg queue from Minions
                while(True):
                    msg = self._syncservice.recv_json(flags=zmq.NOBLOCK)
                    self.msg_handler(msg)
            except Exception as ex:
                #print("No New Msg from Slave!")
                pass
            try:
                # exhaust the msg queue from IPC
                while(True):
                    msg = ipc.recv_json(flags=zmq.NOBLOCK)
                    ipc.send('')
                    self.ipc_handler(msg)
            except Exception as ex:
                #print("No New Msg from IPC!")
                #print ex
                pass
            # check for zombie host
            self._hostmanager.check_hosts()
            time.sleep(self._sleeping)


def etcd_clear(etcdcli):
    """
        Clear etcd database

        @param etcdcli a etcd client object
    """

    try:
        etcdcli.write('/VNF/test', None)
        etcdcli.write('/Host/test', None)
        etcdcli.write('/Chain/test', None)
        etcdcli.write('/source/test', None)
        etcdcli.write('/link_id', None)
        etcdcli.delete("/VNF", recursive=True)
        etcdcli.delete("/Host", recursive=True)
        etcdcli.delete("/Chain", recursive=True)
        etcdcli.delete("/source", recursive=True)
        etcdcli.delete("/link_id")
    except Exception as ex:
        print ex
        traceback.print_exc()


def init_etcd(etcdcli):
    """
        initilize etcd database

        @param etcdcli a etcd client object
    """
    try:
        etcdcli.read('link_id')
    except Exception as ex:
        etcdcli.write('link_id', 0)
    try:
        #etcdcli.delete('/Host', recursive=True)
        etcdcli.write('/Host/test', None)
        etcdcli.delete('/Host/test')
        etcdcli.write('/VNF/test', None)
        etcdcli.delete('/VNF/test')
    except Exception as ex:
        print(ex)
        traceback.print_exc()


def init_zmq(host,pub_port,sync_port):
    """
        initialize zeromq
        
        @param host Interface which master should listen on
        @param Port for publisher (push msg to minion)
        @param sync_port Port for sync (pull msg from minion)
    """
    context = zmq.Context()
    # Socket to broadcast to clients
    publisher = context.socket(zmq.PUB)
    # set SNDHWM, so we don't drop messages for slow subscribers
    publisher.sndhwm = 1100000
    publisher.bind('tcp://'+host+':'+pub_port)
    # Socket to receive signals
    syncservice = context.socket(zmq.PULL)
    syncservice.bind('tcp://'+host+':'+sync_port)
    # Socket to receive IPC
    ipc = context.socket(zmq.REP)
    ipc.bind('ipc:///tmp/test.pipe')
    return publisher, syncservice, ipc

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--clearetcd", help="clear etcd database",
                        action="store_true")
    parser.add_argument("--clearlog", help="clear influx database",
                        action="store_true")
    parser.add_argument("--host", help="Interface which master should listen on",
                        default="0.0.0.0")
    parser.add_argument("--pub_port", help="Port for publisher socket (push msg to minion)",
                        default="5561")
    parser.add_argument("--sync_port", help="Port for sync socket (pull msg from minion)",
                        default="5562")
    parser.add_argument("--sleeping", help="sleeping time while wait new mesg",
                        default=1)
    parser.add_argument("--interval", help="# of seconds before host been marked inactive",
                        default=5)
    args = parser.parse_args()

    # initialize etcd
    etcdcli = etcd.Client()
    if (args.clearetcd):
        etcd_clear(etcdcli)
    init_etcd(etcdcli)
    # initialize influxDB
    influx = logger.influxwrapper()
    if (args.clearlog):
        influx.clear()
    # init zeromq
    publisher, syncservice, ipc = init_zmq(args.host,
                                           args.pub_port,
                                           args.sync_port)
    
    # create ChainManager object
    chainmanager = chain_manager.ChainManager(etcdcli, 
                                              influx, 
                                              publisher, 
                                              syncservice)
    # create HostManager object
    hostmanager = host_manager.HostManager(etcdcli, 
                                           influx, 
                                           syncservice, 
                                           args.interval, 
                                           chainmanager)
    
    # create mastermonitor object
    mastermonitor = MasterMonitor(args.sleeping, 
                                  etcdcli, 
                                  influx, 
                                  publisher, 
                                  syncservice, 
                                  ipc, 
                                  args.interval,
                                  hostmanager,
                                  chainmanager)
    mastermonitor.start()
