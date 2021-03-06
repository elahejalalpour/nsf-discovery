# nsf-discovery
Network Service Function Discovery <br />
[![Build Status](http://cn101.cs.uwaterloo.ca:8080/buildStatus/icon?job=nsf-discovery)](http://cn101.cs.uwaterloo.ca:8080/job/nsf-discovery/) 
[![Coverage Status](http://cn101.cs.uwaterloo.ca:8080/job/nsf-discovery/statusbadges-coverage/icon)](http://cn101.cs.uwaterloo.ca:8080/job/nsf-discovery/) <br />

## Installation
Check the [wiki](https://github.com/WatNFV/nsf-discovery/wiki/Installation-Guide) for installation Guide.

## How to run
Run etcd on the same machine as the master:
```
./etcd --data-dir /var/etcd
```
/var/etcd should have write permission for the current user.

Run master:
```
python master/master.py
```
Run the web server on the same node as the master:
```
python web/server.py
```

Run minion:

```
python minion/daemon.py --master <master's_ip_address> --interface <ethernet_interface_to_use>
```

Use provided chain.json file as the chain configuration. 
Keep the file in location /home/nfuser/chain.json

To deploy a chain use the following curl command:
```
curl -H "Content-Type: application/json" -X POST -d '{"action":"deploy_chain"}' http://localhost:5000/request
```

If master cannot deploy chain for insufficient resources then stop etcd and 
remove the persistant data it is storing:

```
rm -rf /var/etcd/*
```





