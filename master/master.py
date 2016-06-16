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

#  We wait for 2 subscribers
#SUBSCRIBERS_EXPECTED = 2
#sleeping time while wait new mesg

sleeping = 1

def ipc_handler(msg,etcdcli,publisher):
	"""
		handles messages from IPC(tpically commands)
	"""
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
	except Exception,ex:
		print(ex)
	

def msg_handler(msg,etcdcli):
	"""
		handles messages recv from minions
	"""
	#print(msg)
	try:
		if (msg['flag'] == 'REG'):
			print('New Host Registered: '+msg['host'])
			host = {'Host_name' : msg['host'], 'Host_ip' : msg['host_ip'],
						'Host_cpu' : None, 'Host_total_mem' : None,
						'Host_avail_mem' : None,'Host_used_mem' : None,
						'Last_seen' : datetime.now().isoformat(), 'Active' : None, 
						'cpus' : None,'network' : None}
			host = json.dumps(host)
			etcdcli.write('/Host/'+msg['host'],host)
		elif(msg['flag'] == 'sysinfo'):
			host = {'Host_name' : msg['host'], 'Host_ip' : msg['host_ip'],
						'Host_cpu' : msg['cpu'], 'Host_total_mem' : msg['mem_total'],
						'Host_avail_mem' : msg['mem_available'],'Host_used_mem' : msg['used'],
						'Last_seen' : datetime.now().isoformat(), 'Active' : 1,'cpus' : msg['cpus'],
						'network' : msg['network']}
			host = json.dumps(host)
			etcdcli.write('/Host/'+msg['host'],host)
		elif(msg['flag'] == 'new' or msg['flag'] == 'update'):
			if (msg['status'] == 'running'):
				IP = msg['IP']
			else:
				IP = None
			vnf = {'Con_id' : msg['ID'], 'Con_name' : msg['name'],
					'Host_name' : msg['host'], 'VNF_ip' : IP, 
					'VNF_status' : msg['status'], 'VNF_type' : msg['image'],
					'Chain_name' : None, 'net_ifs' : msg['net_ifs']}
			vnf = json.dumps(vnf)
			try:
				r = etcdcli.read('/VNF', recursive=True, sorted=True)
				exist = False
				for child in r.children:
					temp = json.loads(child.value)
					if (temp['Host_name'] == msg['host'] and 
						temp['Con_id'] == msg['ID']):
						exist = True
						etcdcli.write(child.key,vnf)
						break
				if (not exist):
					etcdcli.write("/VNF",vnf,append=True)
			except Exception,ex:
				etcdcli.write("/VNF",vnf,append=True)
				
			#build graph object from chain info
			etcdcli.write('/Chain/test',None)
			etcdcli.delete("/Chain/",recursive=True)
			etcdcli.write('/Chain/test',None)
			etcdcli.delete('/Chain/test')
			r = etcdcli.read('/VNF', recursive=True, sorted=True)
			G=nx.Graph()
			edges = {}
			for child in r.children:
				temp = json.loads(child.value)
				node = temp['Host_name']+'_'+temp['Con_id']
				G.add_node(node)
				lst = temp['net_ifs']
				for val in lst:
					key = val['link_type']+'_'+val['link_id']
					if (edges.has_key(key)):
						edges[key][node] = val['if_name'];
					else:
						edges[key] = {node : val['if_name']}
			#print(edges)
			
			for key in edges:
				if (len(edges[key]) == 2):
					t1 = edges[key].keys();
					t2 = key.split('_')
					G.add_edge(t1[0],t1[1],{'nodes' : edges[key],'link_type' : t2[0],
													'link_id' : t2[1]})
			data = json_graph.node_link_data(G)
			#print(data)
			subgraphs =list(nx.connected_component_subgraphs(G))
			try:
				for g in subgraphs:
					etcdcli.write("/Chain",json_graph.node_link_data(g),append=True)
			except Exception,ex:
				print(ex)
				traceback.print_exc()
			
		else:
			#print(msg)
			pass
		
	except Exception,ex:
		print(ex)
		traceback.print_exc()


def main():
	#interval: how many seconds before been marked inactive
	interval = 5
	#initialize etcd
	etcdcli = etcd.Client()
	try:
		#etcdcli.delete('/Host', recursive=True)
		etcdcli.write('/Host/test',None)
		etcdcli.delete('/Host/test')
		etcdcli.write('/VNF/test',None)
		etcdcli.delete('/VNF/test')
	except Exception,ex:
		print(ex)
		

	#initialize the ZeroMQ
	context = zmq.Context()

	# Socket to broadcast to clients
	publisher = context.socket(zmq.PUB)
	# set SNDHWM, so we don't drop messages for slow subscribers
	publisher.sndhwm = 1100000
	publisher.bind('tcp://*:5561')

	# Socket to receive signals
	syncservice = context.socket(zmq.REP)
	syncservice.bind('tcp://*:5562')
    
	#Socket to receive IPC
	ipc = context.socket(zmq.REP)
	ipc.bind('ipc:///tmp/test.pipe')

	while(True):
		try:
		#exhaust the msg queue from Minions
			while(True):
				msg = syncservice.recv_json(flags=zmq.NOBLOCK)
				syncservice.send('')
				msg_handler(msg,etcdcli)
		except Exception,ex:
			#print("No New Msg from Slave!")
			pass
		try:
		#exhaust the msg queue from IPC
			while(True):
				msg = ipc.recv_json(flags=zmq.NOBLOCK)
				ipc.send('')
				print(msg)
				ipc_handler(msg,etcdcli,publisher)
		except Exception,ex:
			#print("No New Msg from IPC!")
			pass
		#check for zombie host
		try:
			r = etcdcli.read('/Host', recursive=True, sorted=True)
			for child in r.children:
				temp = json.loads(child.value)
				diff = datetime.now() - dateutil.parser.parse(temp['Last_seen'])
				if (temp['Active'] == 1 and diff.seconds > interval):
					temp['Active'] = 0
					hostname = temp['Host_name']
					temp = json.dumps(temp)
					etcdcli.write("/Host/"+hostname,temp)
		except Exception,ex:
			print(ex)
			pass
		time.sleep(sleeping)

if __name__ == '__main__':
    main()
