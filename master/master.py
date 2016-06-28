#
#  Synchronized publisher
#
import zmq
import time
import sqlite3
import json
import etcd
import traceback
import dateutil.parser
from datetime import datetime
import networkx as nx
from networkx.readwrite import json_graph
from copy import deepcopy

#  We wait for 2 subscribers
#SUBSCRIBERS_EXPECTED = 2
# sleeping time while wait new mesg
sleeping = 1


def ipc_handler(msg, etcdcli, publisher):
    """
            handles messages from IPC(typically commands)
    """
    if (msg['action'] == 'create_chain'):
        print json.dumps(msg)
        try:
            chain = {}
            is_possible = True
            hosts = []
            results = etcdcli.read('/Host', recursive=True, sorted=True)
            for child in results.children:
                hosts.append(json.loads(child.value))
            nodes = msg['data']['nodes']
            links = msg['data']['links']

            for node in nodes:
                temp = {'container_name': node['vnf_name'],
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
                link_id = json.loads(etcdcli.read('/link_id').value)
                temp = {'if_name': None,
                        'link_type': None,
                        'link_id': link_id,
                        'tunnel_endpoint': None,
                        'bandwidth': links[link]['bandwidth']}
                temp['if_name'] = 'eth' + \
                    str(chain[links[link]['source']]['net_ifs_num'])
                chain[links[link]['source']]['net_ifs_num'] += 1
                chain[links[link]['source']][
                    'aggregate_band'] += links[link]['bandwidth']
                chain[links[link]['source']]['net_ifs'].append(deepcopy(temp))
                temp['if_name'] = 'eth' + \
                    str(chain[links[link]['target']]['net_ifs_num'])
                chain[links[link]['target']]['net_ifs_num'] += 1
                chain[links[link]['target']][
                    'aggregate_band'] += links[link]['bandwidth']
                chain[links[link]['target']]['net_ifs'].append(deepcopy(temp))
                links[link]['id'] = link_id
                etcdcli.write('/link_id', link_id + 1)

            for ID in chain:
                print ID
                cpu_share = chain[ID]['cpu_share']
                memory = chain[ID]['memory']
                bandwidth = chain[ID]['aggregate_band']
                for host in range(len(hosts)):
                    if (hosts[host]['resource']['memory'] == None):
                        hosts[host]['resource']['memory'] = hosts[
                            host]['Host_avail_mem'] / 1024 / 1024
                    if (memory > hosts[host]['resource']['memory'] or
                            bandwidth > hosts[host]['resource']['bandwidth']):
                        print "Not enough memory\n"
                        continue
                    k = 0
                    for cpu in hosts[host]['resource']['cpus']:
                        print cpu, cpu_share
                        if (cpu < cpu_share):
                            k += 1
                            continue
                        hosts[host]['resource']['cpus'][k] -= cpu_share
                        chain[ID]['cpuset_cpus'] = k
                        break
                    if (chain[ID]['cpuset_cpus'] == None):
                        print "No CPU found\n"
                        continue
                    hosts[host]['resource']['memory'] -= memory
                    hosts[host]['resource']['bandwidth'] -= bandwidth
                    chain[ID]['host'] = hosts[host]['Host_name']
                    chain[ID]['host_ip'] = hosts[host]['Host_ip']
                    break

                if (chain[ID]['host'] == None):
                    is_possible = False
                    break

            if (is_possible):
                # update resource info
                for host in hosts:
                    etcdcli.write(
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
                                    link['source']]['net_ifs'][index]['link_type'] = 'vxlan'
                                chain[link['source']]['net_ifs'][index] \
                                    ['tunnel_endpoint'] = chain[link['target']]['host_ip']
                        target = chain[link['target']]['net_ifs']
                        for index in range(len(target)):
                            if (target[index]['link_id'] == link['id']):
                                chain[
                                    link['target']]['net_ifs'][index]['link_type'] = 'vxlan'
                                chain[link['target']]['net_ifs'][index] \
                                    ['tunnel_endpoint'] = chain[link['source']]['host_ip']
                #chain_list = []
                #for ID in chain:
                #    chain_list.append(chain[ID])
                #print json.dumps(chain_list)
                #publisher.send_json(chain_list)
                publisher.send_json(chain)
                # for ID in chain:
                #	print(chain[ID])
                #	print('############################################')
                #	publisher.send_json(chain[ID])
            else:
                print("Insufficient Resource!")

        except Exception, ex:
            print(ex)
            traceback.print_exc()

    else:
        publisher.send_json(msg)
        try:
            if (msg['action'] == 'destroy'):
                #cur.execute("DELETE FROM VNF WHERE Con_id=? AND Host_name=?",(msg['ID'],msg['host']))
                r = etcdcli.read('/VNF', recursive=True, sorted=True)
                for child in r.children:
                    temp = json.loads(child.value)
                    if (temp['Host_name'] == msg['host'] and
                            temp['Con_id'] == msg['ID']):
                        etcdcli.delete(child.key)
        except Exception, ex:
            print(ex)
            traceback.print_exc()


def msg_handler(msg, etcdcli):
    """
            handles messages recv from minions
    """
    # print(msg)
    try:
        if (msg['flag'] == 'REG'):
            # A new Host joined in the management network
            print('New Host Registered: ' + msg['host'])
            try:
                # entry exists
                host = etcdcli.read('/Host/' + msg['host']).value
                host = json.loads(host)
                host['Host_name'] = msg['host']
                host['Host_ip'] = msg['host_ip']
                host['Host_cpu'] = None
                host['Host_total_mem'] = None
                host['Host_avail_mem'] = None
                host['Host_used_mem'] = None
                host['Last_seen'] = datetime.now().isoformat()
                host['Active'] = None
                host['cpus'] = None
                host['network'] = None
                host['images'] = None
            except Exception, ex:
                # entry does not exist
                resource = {}
                resource['bandwidth'] = 10000
                resource['memory'] = None
                resource['cpus'] = []
                i = 0
                while (i < msg['cpus']):
                    resource['cpus'].append(150)
                    i += 1
                host = {'Host_name': msg['host'], 'Host_ip': msg['host_ip'],
                        'Host_cpu': None, 'Host_total_mem': None,
                        'Host_avail_mem': None, 'Host_used_mem': None,
                        'Last_seen': datetime.now().isoformat(), 'Active': None,
                        'cpus': None, 'network': None, 'images': None, 'resource': resource}
            host = json.dumps(host)
            etcdcli.write('/Host/' + msg['host'], host)
        elif(msg['flag'] == 'sysinfo'):
            # A Host pushed system resource info
            try:
                host = etcdcli.read('/Host/' + msg['host']).value
                host = json.loads(host)
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
            except Exception, ex:
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
                host = {'Host_name': msg['host'], 'Host_ip': msg['host_ip'],
                        'Host_cpu': msg['cpu'], 'Host_total_mem': msg['mem_total'],
                        'Host_avail_mem': msg['mem_available'], 'Host_used_mem': msg['used'],
                        'Last_seen': datetime.now().isoformat(), 'Active': 1, 'cpus': msg['cpus'],
                        'network': msg['network'], 'images': msg['images'], 'resource': resource}

            host = json.dumps(host)
            etcdcli.write('/Host/' + msg['host'], host)
        elif(msg['flag'] == 'new' or msg['flag'] == 'update'):
            # A new VNF is detected or a status change in existing VNF
            if (msg['status'] == 'running'):
                IP = msg['IP']
            else:
                IP = None
            vnf = {'Con_id': msg['ID'], 'Con_name': msg['name'],
                   'Host_name': msg['host'], 'VNF_ip': IP,
                   'VNF_status': msg['status'], 'VNF_type': msg['image'],
                   'Chain_name': None, 'net_ifs': msg['net_ifs']}
            vnf = json.dumps(vnf)
            try:
                r = etcdcli.read('/VNF', recursive=True, sorted=True)
                exist = False
                for child in r.children:
                    temp = json.loads(child.value)
                    if (temp['Host_name'] == msg['host'] and
                            temp['Con_id'] == msg['ID']):
                        exist = True
                        etcdcli.write(child.key, vnf)
                        break
                if (not exist):
                    etcdcli.write("/VNF", vnf, append=True)
            except Exception, ex:
                etcdcli.write("/VNF", vnf, append=True)

            # build graph object from chain info when the VNF status changed
            etcdcli.write('/Chain/test', None)
            etcdcli.delete("/Chain/", recursive=True)
            etcdcli.write('/Chain/test', None)
            etcdcli.delete('/Chain/test')
            r = etcdcli.read('/VNF', recursive=True, sorted=True)
            G = nx.Graph()
            edges = {}
            for child in r.children:
                temp = json.loads(child.value)
                node = temp['Host_name'] + '_' + temp['Con_id']
                G.add_node(node)
                lst = temp['net_ifs']
                for val in lst:
                    key = val['link_type'] + '_' + val['link_id']
                    if (edges.has_key(key)):
                        edges[key][node] = val['if_name']
                    else:
                        edges[key] = {node: val['if_name']}
            # print(edges)
            '''
				nodes : [{HostX_VNFX:ethX},{HostX_VNFX:ethX}]
				edges : {nodes,link_type,link_id}
			'''
            for key in edges:
                if (len(edges[key]) == 2):
                    t1 = edges[key].keys()
                    t2 = key.split('_')
                    G.add_edge(t1[0], t1[1], {'nodes': edges[key], 'link_type': t2[0],
                                              'link_id': t2[1]})
            data = json_graph.node_link_data(G)
            # print(data)
            subgraphs = list(nx.connected_component_subgraphs(G))
            try:
                for g in subgraphs:
                    etcdcli.write(
                        "/Chain",
                        json_graph.node_link_data(g),
                        append=True)
            except Exception, ex:
                print(ex)
                traceback.print_exc()

        else:
            # print(msg)
            pass

    except Exception, ex:
        print(ex)
        traceback.print_exc()


def main():
    # interval: how many seconds before been marked inactive
    interval = 5
    # initialize etcd
    etcdcli = etcd.Client()
    try:
        etcdcli.read('link_id')
    except Exception, ex:
        etcdcli.write('link_id', 0)
    try:
        #etcdcli.delete('/Host', recursive=True)
        etcdcli.write('/Host/test', None)
        etcdcli.delete('/Host/test')
        etcdcli.write('/VNF/test', None)
        etcdcli.delete('/VNF/test')
    except Exception, ex:
        print(ex)
        traceback.print_exc()

    # initialize the ZeroMQ
    context = zmq.Context()

    # Socket to broadcast to clients
    publisher = context.socket(zmq.PUB)
    # set SNDHWM, so we don't drop messages for slow subscribers
    publisher.sndhwm = 1100000
    publisher.bind('tcp://*:5561')

    # Socket to receive signals
    syncservice = context.socket(zmq.REP)
    syncservice.bind('tcp://*:5562')

    # Socket to receive IPC
    ipc = context.socket(zmq.REP)
    ipc.bind('ipc:///tmp/test.pipe')

    while(True):
        try:
            # exhaust the msg queue from Minions
            while(True):
                msg = syncservice.recv_json(flags=zmq.NOBLOCK)
                syncservice.send('')
                msg_handler(msg, etcdcli)
        except Exception, ex:
            #print("No New Msg from Slave!")
            pass
        try:
            # exhaust the msg queue from IPC
            while(True):
                msg = ipc.recv_json(flags=zmq.NOBLOCK)
                ipc.send('')
                # print(msg)
                ipc_handler(msg, etcdcli, publisher)
        except Exception, ex:
            #print("No New Msg from IPC!")
            pass
        # check for zombie host
        try:
            r = etcdcli.read('/Host', recursive=True, sorted=True)
            for child in r.children:
                temp = json.loads(child.value)
                diff = datetime.now() - \
                    dateutil.parser.parse(temp['Last_seen'])
                if (temp['Active'] == 1 and diff.seconds > interval):
                    temp['Active'] = 0
                    hostname = temp['Host_name']
                    temp = json.dumps(temp)
                    etcdcli.write("/Host/" + hostname, temp)
        except Exception, ex:
            print(ex)
            traceback.print_exc()
            pass
        time.sleep(sleeping)

if __name__ == '__main__':
    main()
