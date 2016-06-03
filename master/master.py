#
#  Synchronized publisher
#
import zmq
import time
import sqlite3
import json

#  We wait for 2 subscribers
#SUBSCRIBERS_EXPECTED = 2

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
	

def msg_handler(msg,cur):
	"""
		handles messages recv from minions
	"""
	#print(msg)
	try:
		if (msg['flag'] == 'REG'):
			print('New Host Registered: '+msg['host'])
			cur.execute("INSERT INTO Host VALUES(?,?,?,?,?,?)",
							(msg['host'],msg['host_ip'],None,None,None,None))
		elif(msg['flag'] == 'sysinfo'):
			cur.execute("""UPDATE Host SET Host_cpu = ? ,
							Host_total_mem = ?,Host_avail_mem = ?,
							Host_used_mem = ? WHERE Host_name= ?""",
							(msg['cpu'],msg['mem_total'],msg['mem_available'],
							msg['used'],msg['host']))
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
				msg_handler(msg,cur)
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
		time.sleep(1)

if __name__ == '__main__':
    main()
