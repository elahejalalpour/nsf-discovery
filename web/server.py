from flask import Flask
from flask import request
from flask import jsonify
import json
import sqlite3
import command
import etcd

cmd = command.CMD()

etcdcli = etcd.Client()


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
    try:
        results = []
        r = etcdcli.read('/VNF', recursive=True, sorted=True)
        for child in r.children:
            results.append(json.loads(child.value))
        return jsonify(results)
    except:
        print "Error retrieving VNFs"
        return jsonify([])


@app.route('/getHost', methods=['GET'])
def send_Host():
    # cur.execute('select * from Host')
    # results = cur.fetchall()
    results = []
    r = etcdcli.read('/Host', recursive=True, sorted=True)
    for child in r.children:
        results.append(json.loads(child.value))
    return jsonify(results)


@app.route('/getChain', methods=['GET'])
def send_Chain():
    try:
        results = []
        r = etcdcli.read('/Chain', recursive=True, sorted=True)
        for child in r.children:
            child_json = json.loads(child.value)
            results.append(child_json)
        return jsonify(results)
    except:
        print "Error occured while getting chain data"
        return jsonify([])


@app.route('/request', methods=['POST'])
def reply():
    msg = request.get_json()
    print(msg)
    if (msg['action'] == 'start'):
        cmd.start(msg['Host'], msg['ID'])
    elif(msg['action'] == 'stop'):
            cmd.stop(msg['Host'], msg['ID'])
    elif(msg['action'] == 'restart'):
        cmd.restart(msg['Host'], msg['ID'])
    elif(msg['action'] == 'destroy'):
        cmd.destroy(msg['Host'], msg['ID'])
    elif(msg['action'] == 'pause'):
        cmd.pause(msg['Host'], msg['ID'])
    elif(msg['action'] == 'unpause'):
        cmd.unpause(msg['Host'], msg['ID'])
    elif(msg['action'] == 'deploy'):
        cmd.deploy(msg['Host'], msg['username'], msg['image'], msg['vnfname'])
    # elif(msg['action'] == 'deploy_chain'):
    #    cmd.create_chain()

    return jsonify({'result' : 'command received'})

@app.route('/create_chain', methods = ['POST'])
def create_chain():
    config_json = request.files['file'].stream.read()
    cmd.create_chain(config_json)
    return jsonify({'result' : 'command received'})

if __name__ == "__main__":
    app.run()
