from flask import Flask
from flask import request
from flask import jsonify
import json
import sqlite3
import command

#set up database connection
conn = sqlite3.connect('../master/vnfs.db')
cur = conn.cursor()

cmd = command.CMD()


app = Flask(__name__)

@app.route('/', methods=['GET'])
    
def root():
	return app.send_static_file('index.html')
    
@app.route('/js/monitor.js')
def send_monitor():
	return app.send_static_file('js/monitor.js')
    
@app.route('/js/model.js')
def send_model():
	return app.send_static_file('js/model.js')
    
@app.route('/css/monitor.css')
def send_css():
	return app.send_static_file('css/monitor.css')
    
@app.route('/getVNF', methods=['GET'])
def send_VNF():
	cur.execute('select * from VNF')
	results = cur.fetchall()
	return jsonify(results)

@app.route('/getHost', methods=['GET', 'POST'])
def send_Host():
	cur.execute('select * from Host')
	results = cur.fetchall()
	return jsonify(results)
	
@app.route('/request', methods=['POST'])
def reply():
	msg = request.get_json()
	print(msg)
	if (msg['action'] == 'start'):
		cmd.start(msg['Host'],msg['ID'])
	elif(msg['action'] == 'stop'):
			cmd.stop(msg['Host'],msg['ID'])
	elif(msg['action'] == 'restart'):
		cmd.restart(msg['Host'],msg['ID'])
	elif(msg['action'] == 'destroy'):
		cmd.destroy(msg['Host'],msg['ID'])
	elif(msg['action'] == 'pause'):
		cmd.pause(msg['Host'],msg['ID'])
	elif(msg['action'] == 'unpause'):
		cmd.unpause(msg['Host'],msg['ID'])
		
	return jsonify({'result' : 'command received'})

if __name__ == "__main__":
	app.run()
