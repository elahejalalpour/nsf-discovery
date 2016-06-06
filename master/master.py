#
#  Synchronized publisher
#
import zmq
import time
import sqlite3
import json

#  We wait for 2 subscribers
#SUBSCRIBERS_EXPECTED = 2
#sleeping time while wait new mesg

sleeping = 1
global seq

def ipc_handler(msg,cur,publisher):
	"""
		handles messages from IPC(tpically commands)
	"""
	publisher.send_json(msg)
	try:
		if (msg['action'] == 'destroy'):
			cur.execute("DELETE FROM VNF WHERE Con_id=? AND Host_name=?",(msg['ID'],msg['host']))
	except Exception,ex:
		print(ex)
	

def msg_handler(msg,cur,seq):
	"""
		handles messages recv from minions
	"""
	#print(msg)
	try:
		if (msg['flag'] == 'REG'):
			print('New Host Registered: '+msg['host'])
			cur.execute("DELETE FROM Host WHERE Host_name = ?",(msg['host'],))
			cur.execute("INSERT INTO Host VALUES(?,?,?,?,?,?,?,?)",
							(msg['host'],msg['host_ip'],None,None,None,None,None,1))
		elif(msg['flag'] == 'sysinfo'):
			cur.execute("""UPDATE Host SET Host_cpu = ? ,
							Host_total_mem = ?,Host_avail_mem = ?,
							Host_used_mem = ?,Last_seen = ?,
							Active = ? WHERE Host_name= ?""",
							(msg['cpu'],msg['mem_total'],msg['mem_available'],
							msg['used'],seq,1,msg['host']))
		elif(msg['flag'] == 'new'):
			if (msg['status'] == 'running'):
				IP = msg['IP']
			else:
				IP = None
			cur.execute("INSERT INTO VNF VALUES(?,?,?,?,?,?,?)",
							(msg['ID'],msg['name'],msg['host'],IP,msg['status'],
							 msg['image'],None))
			
		elif(msg['flag'] == 'update'):
			if (msg['status'] == 'running'):
				IP = msg['IP']
			else:
				IP = None
			cur.execute("""UPDATE VNF SET VNF_status = ? ,
							VNF_ip = ? WHERE Host_name= ? AND Con_id = ?""",
							(msg['status'],IP,msg['host'],msg['ID']))
		else:
			#print(msg)
			pass
	except Exception,ex:
		print(ex)


def main():
	#sequence number for alive check,
	#interval: how many updates can a host miss before been marked inactive
	seq = 0
	interval = 30
	#initialize the sqlite database
	conn = sqlite3.connect('vnfs.db')
	cur = conn.cursor()
	schema = open('schema.sql', 'r').read()
	cur.executescript(schema)
	conn.commit()

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
				msg_handler(msg,cur,seq)
				conn.commit()
		except Exception,ex:
			#print("No New Msg from Slave!")
			pass
		try:
		#exhaust the msg queue from IPC
			while(True):
				msg = ipc.recv_json(flags=zmq.NOBLOCK)
				ipc.send('')
				print(msg)
				ipc_handler(msg,cur,publisher)
		except Exception,ex:
			#print("No New Msg from IPC!")
			pass
		#check for zombie host
		cur.execute("""UPDATE Host SET Active = 0 
							WHERE abs(Last_seen - ?) > ? AND Active = 1""",
							(seq,interval))
		if (seq < 500):
			seq = seq + 1
		else:
			seq = 0
		time.sleep(sleeping)

if __name__ == '__main__':
    main()
