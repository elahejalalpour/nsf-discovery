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
from copy import deepcopy
import logger

class HostManager():
    def __init__(self, etcdcli, influx, syncservice, interval, chainmanager):
        self._etcdcli = etcdcli
        self._influx = influx
        self._syncservice = syncservice
        self._interval = interval
        self._chainmanager = chainmanager
        
    def host_register(self, msg):
        """
            Register host with master

            @param msg a valid message from minion
        """
        try:
            # entry exists--> minion failed and restarted
            host = self._etcdcli.read('/Host/' + msg['host']).value
            host = json.loads(host)
            host['Host_name'] = msg['host']
            host['Host_ip'] = msg['host_ip']
            host['Host_cpu'] = None
            host['Host_total_mem'] = None
            host['Host_avail_mem'] = None
            host['Host_used_mem'] = None
            host['Last_seen'] = datetime.now().isoformat()
            host['Active'] = True
            host['cpus'] = None
            host['network'] = None
            host['images'] = None
            self._influx.log_host(host['Host_name'],
                                  host['Host_ip'],
                                  'reconnected')
        except Exception as ex:
            # entry does not exist --> minion first time connected to master
            resource = {}
            resource['bandwidth'] = 10000
            resource['memory'] = None
            resource['cpus'] = []
            i = 0
            while (i < msg['cpus']):
                resource['cpus'].append(150)
                i += 1
            host = {'Host_name': msg['host'],
                    'Host_ip': msg['host_ip'],
                    'Host_cpu': None,
                    'Host_total_mem': None,
                    'Host_avail_mem': None,
                    'Host_used_mem': None,
                    'Last_seen': datetime.now().isoformat(),
                    'Active': True,
                    'cpus': None,
                    'network': None,
                    'images': None,
                    'resource': resource}

            self._influx.log_host(host['Host_name'],
                                  host['Host_ip'],
                                  'registered')
        host = json.dumps(host)
        self._etcdcli.write('/Host/' + msg['host'], host)

    def update_host(self, msg):
        """
            Update host info stored in etcd

            @param msg a valid message from minion
        """
        try:
            host = self._etcdcli.read('/Host/' + msg['host']).value
            host = json.loads(host)
            # minion lost connection for a while,
            # should ask minion push all VNF info
            if (not host['Active']):
                self._chainmanager.report(host['Host_name')
                self._influx.log_host(host['Host_name'],
                                      host['Host_ip'],
                                      'reconnected')

            host['Host_name'] = msg['host']
            host['Host_ip'] = msg['host_ip']
            host['Host_cpu'] = msg['cpu']
            host['Host_total_mem'] = msg['mem_total']
            host['Host_avail_mem'] = msg['mem_available']
            host['Host_used_mem'] = msg['used']
            host['Last_seen'] = datetime.now().isoformat()
            host['Active'] = 1
            host['cpus'] = msg['cpus']
            host['network'] = msg['network']
            host['images'] = msg['images']
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            resource = {}
            resource['bandwidth'] = 10000
            resource['memory'] = None
            resource['cpus'] = []
            i = 0
            while (i < len(msg['cpus'])):
                resource['cpus'].append(150)
                i += 1
            host = {'Host_name': msg['host'],
                    'Host_ip': msg['host_ip'],
                    'Host_cpu': msg['cpu'],
                    'Host_total_mem': msg['mem_total'],
                    'Host_avail_mem': msg['mem_available'],
                    'Host_used_mem': msg['used'],
                    'Last_seen': datetime.now().isoformat(),
                    'Active': 1, 'cpus': msg['cpus'],
                    'network': msg['network'],
                    'images': msg['images'],
                    'resource': resource}

        self._influx.log_cpu(host['Host_name'], host['Host_cpu'])

        self._influx.log_mem(host['Host_name'],
                             host['Host_used_mem'] / host['Host_total_mem'])
        host = json.dumps(host)
        self._etcdcli.write('/Host/' + msg['host'], host)
        
    def check_hosts(self):
        """
            Mark zombie hosts and break chain if it contains vnf located
            on the zombie host

        """

        try:
            hosts = self._etcdcli.read('/Host', recursive=True, sorted=True)
            for host in hosts.children:
                temp = json.loads(host.value)
                diff = datetime.now() - \
                    dateutil.parser.parse(temp['Last_seen'])
                if (temp['Active'] == 1 and diff.seconds > self._interval):
                    temp['Active'] = 0
                    hostname = temp['Host_name']
                    self._influx.log_host(temp['Host_name'],
                                          temp['Host_ip'],
                                          'inactive')
                    temp = json.dumps(temp)
                    self._etcdcli.write("/Host/" + hostname, temp)
                    try:
                        VNF = self._etcdcli.read(
                            '/VNF', recursive=True, sorted=True)
                        for vnf in VNF.children:
                            temp = json.loads(vnf.value)
                            vnf_name = temp['Con_name']
                            if (temp['Host_name'] == hostname):
                                temp['status'] = 'Unknown'
                                self._etcdcli.write('/VNF/'+vnf.key,
                                                    json.dumps(temp))
                                self._influx.log_vnf(temp['Con_id'],
                                                     temp['VNF_type'],
                                                     hostname,
                                                     'Host Inactive')
                                # any chain contain this vnf should be marked
                                # as unavailable
                                self._chainmanager.check_chain(
                                    hostname + '_' + temp['Con_id'] + '_' + vnf_name.split('_')[-1])
                    except Exception as ex:
                        print(ex)
                        traceback.print_exc()
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            pass
