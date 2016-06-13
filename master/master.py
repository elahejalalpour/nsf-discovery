#
#  Synchronized publisher
#
import zmq
import time
import sqlite3
import json
import etcd
import traceback

#  We wait for 2 subscribers
#SUBSCRIBERS_EXPECTED = 2
#sleeping time while wait new mesg

sleeping = 1
global seq

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
	

def msg_handler(msg,etcdcli,seq):
	"""
		handles messages recv from minions
	"""
	#print(msg)
	try:
		if (msg['flag'] == 'REG'):
			print('New Host Registered: '+msg['host'])
			'''
			cur.execute("DELETE FROM Host WHERE Host_name = ?",(msg['host'],))
			cur.execute("INSERT INTO Host VALUES(?,?,?,?,?,?,?,?)",
							(msg['host'],msg['host_ip'],None,None,None,None,None,1))
			'''
			host = {'Host_name' : msg['host'], 'Host_ip' : msg['host_ip'],
						'Host_cpu' : None, 'Host_total_mem' : None,
						'Host_avail_mem' : None,'Host_used_mem' : None,
						'Last_seen' : None, 'Active' : None, 'cpus' : None,
						'network' : None}
			host = json.dumps(host)
			etcdcli.write('/Host/'+msg['host'],host)
		elif(msg['flag'] == 'sysinfo'):
			'''
			cur.execute("""UPDATE Host SET Host_cpu = ? ,
							Host_total_mem = ?,Host_avail_mem = ?,
							Host_used_mem = ?,Last_seen = ?,
							Active = ? WHERE Host_name= ?""",
							(msg['cpu'],msg['mem_total'],msg['mem_available'],
							msg['used'],seq,1,msg['host']))
			'''
			host = {'Host_name' : msg['host'], 'Host_ip' : msg['host_ip'],
						'Host_cpu' : msg['cpu'], 'Host_total_mem' : msg['mem_total'],
						'Host_avail_mem' : msg['mem_available'],'Host_used_mem' : msg['used'],
						'Last_seen' : seq, 'Active' : 1,'cpus' : msg['cpus'],
						'network' : msg['network']}
			host = json.dumps(host)
			etcdcli.write('/Host/'+msg['host'],host)
		elif(msg['flag'] == 'new' or msg['flag'] == 'update'):
			if (msg['status'] == 'running'):
				IP = msg['IP']
			else:
				IP = None
			'''
			cur.execute("INSERT INTO VNF VALUES(?,?,?,?,?,?,?)",
							(msg['ID'],msg['name'],msg['host'],IP,msg['status'],
							 msg['image'],None))
			'''
			vnf = {'Con_id' : msg['ID'], 'Con_name' : msg['name'],
					'Host_name' : msg['host'], 'VNF_ip' : IP, 
					'VNF_status' : msg['status'], 'VNF_type' : msg['image'],
					'Chain_name' : None}
			vnf = json.dumps(vnf)
			try:
				etcdcli.delete('/VNF/test')
				etcdcli.write("/VNF",vnf,append=True)
			except Exception,ex:
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
			
		else:
			#print(msg)
			pass
	except Exception,ex:
		print(ex)
		traceback.print_exc()


def main():
	#sequence number for alive check,
	#interval: how many updates can a host miss before been marked inactive
	seq = 0
	interval = 30
	#initialize the sqlite database
	'''
	conn = sqlite3.connect('vnfs.db')
	cur = conn.cursor()
	schema = open('schema.sql', 'r').read()
	cur.executescript(schema)
	conn.commit()
	'''
	
	#initialize etcd
	etcdcli = etcd.Client()
	try:
		#etcdcli.delete('/Host', recursive=True)
		etcdcli.write('/Host/test',None)
		etcdcli.delete('/Host/test')
		etcdcli.write('/VNF/test',None)
		etcdcli.delete('/VNF/test')
		etcdcli.write('/Chain/test',None)
		etcdcli.delete('/Chain/test')
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
				msg_handler(msg,etcdcli,seq)
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
		'''
		cur.execute("""UPDATE Host SET Active = 0 
							WHERE abs(Last_seen - ?) > ? AND Active = 1""",
							(seq,interval))
		'''
		try:
			r = etcdcli.read('/Host', recursive=True, sorted=True)
			for child in r.children:
				temp = json.loads(child.value)
				if (temp['Active'] == 1 and (abs(temp['Last_seen'] - seq)) > interval):
					temp['Active'] = 0
					hostname = temp['Host_name']
					temp = json.dumps(temp)
					etcdcli.write("/Host/"+hostname,temp)
		except Exception,ex:
			print(ex)
			pass
		if (seq < 500):
			seq = seq + 1
		else:
			seq = 0
		#conn.commit()
		time.sleep(sleeping)

if __name__ == '__main__':
    main()
