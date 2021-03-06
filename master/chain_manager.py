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
import logger
import uuid

class ChainManager():
    def __init__(self, etcdcli, influx, publisher, syncservice):
        self._etcdcli = etcdcli
        self._influx = influx
        self._publisher = publisher
        self._syncservice = syncservice
    
    def report(self,host):
        """
            Force a host to report all VNF info
        """
        msg = {'host' : host, 'action' : 'report'}
        self._publisher.send_json(msg)
    
    def create_chain(self, mssg):
        """
            Create chain from a json query

            @param mssg a valid json message contain chain info
        """
        try:
            base_ip = ipaddress.ip_address(u'192.168.0.2')
            chain = {}
            is_possible = True
            hosts = []
            results = self._etcdcli.read('/Host', recursive=True, sorted=True)
            for child in results.children:
                hosts.append(json.loads(child.value))
            print hosts
            nodes = mssg['data']['nodes']
            links = mssg['data']['links']

            unique = str(uuid.uuid4())
            for node in nodes:
                temp = {'container_name': node['vnf_name'] + '_' + unique,
                        'cpu_share': node['cpu_share'],
                        'cpuset_cpus': None,
                        'memory': node['memory'],
                        'aggregate_band': 0,
                        'vnf_type': node['vnf_type'],
                        'action': 'create_chain',
                        'host': None,
                        'host_ip': None,
                        'net_ifs_num': 0,
                        'net_ifs': []}
                chain[node['id']] = temp

            for link in range(len(links)):
                k = 0
                link_id = json.loads(self._etcdcli.read('/link_id').value)
                temp = {'if_name': None,
                        'link_type': None,
                        'link_id': link_id,
                        'tunnel_endpoint': None,
                        'bandwidth': links[link]['bandwidth'],
                        'ip_address': str(base_ip + k) + "/24"}
                k = k + 1
                temp['if_name'] = 'eth' + \
                    str(chain[links[link]['source']]['net_ifs_num'])
                chain[links[link]['source']]['net_ifs_num'] += 1
                chain[links[link]['source']][
                    'aggregate_band'] += links[link]['bandwidth']
                chain[links[link]['source']]['net_ifs'].append(deepcopy(temp))
                self._etcdcli.write('/source/ip_address', temp['ip_address'])
                temp['if_name'] = 'eth' + \
                    str(chain[links[link]['target']]['net_ifs_num'])
                chain[links[link]['target']]['net_ifs_num'] += 1
                chain[links[link]['target']][
                    'aggregate_band'] += links[link]['bandwidth']
                temp['ip_address'] = str(base_ip + k) + "/24"
                k = k + 256
                chain[links[link]['target']]['net_ifs'].append(deepcopy(temp))
                links[link]['id'] = link_id
                self._etcdcli.write('/link_id', link_id + 1)
                self._etcdcli.write('/target/ip_address', temp['ip_address'])

            unique_hosts = set()
            for ID in chain:
                cpu_share = chain[ID]['cpu_share']
                memory = chain[ID]['memory']
                bandwidth = chain[ID]['aggregate_band']
                for host in range(len(hosts)):
                    if (hosts[host]['resource']['memory'] is None):
                        hosts[host]['resource']['memory'] = hosts[
                            host]['Host_avail_mem'] / 1024 / 1024
                    avail_memory = hosts[host]['Host_avail_mem'] / 1024 / 1024
                    if (memory > avail_memory or
                            bandwidth > hosts[host]['resource']['bandwidth']):
                        print "Not enough memory/bandwidth\n"
                        continue
                    k = 0
                    print hosts[host]['resource']['cpus']
                    print cpu_share
                    for cpu in hosts[host]['resource']['cpus']:
                        if (cpu < cpu_share):
                            k += 1
                            continue
                        hosts[host]['resource']['cpus'][k] -= cpu_share
                        chain[ID]['cpuset_cpus'] = k
                        break
                    if (chain[ID]['cpuset_cpus'] is None):
                        print "No CPU found\n"
                        continue
                    hosts[host]['resource']['memory'] = avail_memory - memory
                    hosts[host]['resource']['bandwidth'] -= bandwidth
                    chain[ID]['host'] = hosts[host]['Host_name']
                    chain[ID]['host_ip'] = hosts[host]['Host_ip']
                    unique_hosts.add(chain[ID]['host'])
                    break

                if (chain[ID]['host'] is None):
                    is_possible = False
                    break

            if (is_possible):
                # update resource info
                for host in hosts:
                    self._etcdcli.write(
                        '/Host/' +
                        host['Host_name'],
                        json.dumps(host))

                for link in links:
                    if (chain[link['source']]['host'] ==
                            chain[link['target']]['host']):
                        source = chain[link['source']]['net_ifs']
                        for index in range(len(source)):
                            if (source[index]['link_id'] == link['id']):
                                chain[
                                    link['source']]['net_ifs'][index]['link_type'] = 'local'
                        target = chain[link['target']]['net_ifs']
                        for index in range(len(target)):
                            if (target[index]['link_id'] == link['id']):
                                chain[
                                    link['target']]['net_ifs'][index]['link_type'] = 'local'
                    else:
                        source = chain[link['source']]['net_ifs']
                        for index in range(len(source)):
                            if (source[index]['link_id'] == link['id']):
                                chain[
                                    link['source']]['net_ifs'][index]['link_type'] = 'gre'
                                chain[link['source']]['net_ifs'][index] \
                                    ['tunnel_endpoint'] = chain[link['target']]['host_ip']
                                targets = chain[link['target']]['net_ifs']
                                for idx in range(len(targets)):
                                    if targets[idx]['link_id'] == source[
                                            index]['link_id']:
                                        source[index]['remote_container_ip'] = targets[
                                            idx]['ip_address']
                                        break

                        target = chain[link['target']]['net_ifs']
                        for index in range(len(target)):
                            if (target[index]['link_id'] == link['id']):
                                chain[
                                    link['target']]['net_ifs'][index]['link_type'] = 'gre'
                                chain[link['target']]['net_ifs'][index] \
                                    ['tunnel_endpoint'] = chain[link['source']]['host_ip']
                                sources = chain[link['source']]['net_ifs']
                                for idx in range(len(sources)):
                                    if sources[idx]['link_id'] == target[
                                            index]['link_id']:
                                        target[index]['remote_container_ip'] = sources[
                                            idx]['ip_address']
                                        break

                for host in unique_hosts:
                    message = {
                        'action': 'create_chain', 'host': host, 'data': []}
                    for ID in chain:
                        if chain[ID]['host'] == host:
                            message['data'].append(chain[ID])
                    self._publisher.send_json(message)
            else:
                print("Insufficient Resource!")

        except Exception as ex:
            print(ex)
            traceback.print_exc()
            
    def check_chain(self, node_name):
        '''
            @param node_name node name of a vnf
            @brief check any chain contains this vnf
        '''
        try:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            chains = self._etcdcli.read('/Chain', recursive=True, sorted=True)
            for chain in chains.children:
                temp = json_graph.node_link_graph(json.loads(chain.value))
                nodes = temp.nodes()
                contain = False
                print "nodes:"
                print nodes
                for node in nodes:
                    print(node_name)
                    print(node)
                    if (node == node_name):
                        contain = True
                if (contain and temp.graph['available'] == True):
                    temp.graph['available'] = False
                    self._etcdcli.write("/Chain/" + node_name.split('_')[-1],
                                        json.dumps(json_graph.node_link_data(temp)))
                    self._influx.log_chain(temp.graph['chain_id'], 'broken')
        except Exception as ex:
            print(ex)
            traceback.print_exc()

    def update_vnf(self, msg):
        """
            Update vnf info stored in etcd and log

            @param msg a valid message from minion
        """

        if (msg['status'] == 'running'):
            IP = msg['IP']
        else:
            IP = None
        vnf = {'Con_id': msg['ID'], 'Con_name': msg['name'],
               'Host_name': msg['host'], 'VNF_ip': IP,
               'VNF_status': msg['status'], 'VNF_type': msg['image'],
               'Chain_name': None, 'net_ifs': msg['net_ifs']}
        vnf = json.dumps(vnf)
        print "VNF info received:"
        print vnf
        try:
            r = self._etcdcli.read('/VNF', recursive=True, sorted=True)
            exist = False
            for child in r.children:
                temp = json.loads(child.value)
                if (temp['Host_name'] == msg['host'] and
                        temp['Con_id'] == msg['ID']):
                    exist = True
                    self._etcdcli.write('/VNF/' + child.key, vnf)
                    break
            if (not exist):
                self._etcdcli.write("/VNF", vnf, append=True)
        except Exception as ex:
            self._etcdcli.write("/VNF", vnf, append=True)

        self._influx.log_vnf(msg['ID'],
                             msg['image'],
                             msg['host'],
                             msg['status'])
        # check broken chains
        if (msg['status'] != 'running'):
            self.check_chain(msg['host'] + '_' + msg['ID'] +
                             '_' + msg['name'].split('_')[-1])

    def construct_chain(self):
        """
            Construct chain by using info stored in /VNF
            only running vnf are considered

        """
        # build graph object from chain info when the VNF status changed
        self._etcdcli.write('/Chain/test', None)
        self._etcdcli.delete('/Chain/test')
        r = self._etcdcli.read('/VNF', recursive=True, sorted=True)
        G = nx.Graph()
        edges = {}
        for child in r.children:
            #print "Child: "
            #print child
            temp = json.loads(child.value)
            #print "Child JSON: "
            #print temp
            if (temp['VNF_status'] == 'running'):
                node = temp['Host_name'] + '_' + temp['Con_id'] + \
                    '_' + temp['Con_name'].split('_')[-1]
                G.add_node(node, name=temp['Con_name'], type=temp['VNF_type'])
                lst = temp['net_ifs']
                #print "lst:"
                #print lst
                for val in lst:
                    #print "val:"
                    #print val
                    key = val['link_type'] + '_' + val['link_id']
                    if (key in edges):
                        edges[key][node] = val['if_name']
                    else:
                        edges[key] = {node: val['if_name']}
        # print(edges)
        '''
            nodes : [{HostX_VNFX_chain_id:ethX},{HostX_VNFX_chain_id:ethX}]
            edges : {nodes,link_type,link_id}
        '''
        for key in edges:
            if (len(edges[key]) == 2):
                t1 = edges[key].keys()
                t2 = key.split('_')
                G.add_edge(t1[0], t1[1], {'nodes': edges[key], 'link_type': t2[0],
                                          'link_id': t2[1]})
        data = json_graph.node_link_data(G)
        print 'chain construction'
        print(data)
        subgraphs = list(nx.connected_component_subgraphs(G))
        try:
            for g in subgraphs:
                g.graph['available'] = True
                g.graph['Last_seen'] = datetime.now().isoformat()
                nodesA = set(g.nodes())
                chain_id = g.nodes()[0].split('_')[-1]
                g.graph['chain_id'] = chain_id
                try:
                    r = self._etcdcli.read("/Chain/" + chain_id)
                    temp = json_graph.node_link_graph(json.loads(r.value))
                    nodesB = set(temp.nodes())
                    if (nodesB.issubset(nodesA)):
                        print "nodeA:"
                        print nodesA
                        print "nodeB:"
                        print nodesB
                        self._etcdcli.write("/Chain/" + chain_id,
                                            json.dumps(json_graph.node_link_data(g)))
                        self._influx.log_chain(chain_id, 'updated')
                    #r = self._etcdcli.read("/Chain", recursive=True, sorted=True)
                    #exist = False
                    # for child in r.children:
                    #    temp = json_graph.node_link_graph(json.loads(child.value))
                    #    nodesB = set(temp.nodes())
                    #    if (nodesA == nodesB):
                    #        exist = True
                    #        self._etcdcli.write("/Chain/"+chain_id,
                    #                  json.dumps(json_graph.node_link_data(g)))
                    #        influx.log_chain(chain_id,'updated')

                    # if (not exist):
                    #    self._etcdcli.write("/Chain",
                    #                  json.dumps(json_graph.node_link_data(g)),
                    #                  append=True)
                    #    self._influx.log_chain(chain_id,'created')
                except Exception as ex:
                    print ex
                    traceback.print_exc()
                    self._etcdcli.write("/Chain/" + chain_id,
                                        json.dumps(json_graph.node_link_data(g)))
                    self._influx.log_chain(chain_id, 'created')
                    # self._etcdcli.write(
                    #    "/Chain",
                    #    json.dumps(json_graph.node_link_data(g)),
                    #    append=True)
                    # self._influx.log_chain(chain_id,'created')
        except Exception as ex:
            print(ex)
            traceback.print_exc()
