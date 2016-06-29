# nsf-discovery
Network Service Function Discovery <br />
on master:<br />
zeromq <br />
flask <br />
python-dateutil <br />
networkx <br />

On minion: <br />
psutil <br />
zeromq <br />

required python packages: zmq, psutil, rollbackcontext, flask, python-dateutil,
networkx, etcd<br />

Run etcd on the same machine as the master:
```
./etcd --data-dir /var/etcd
```
/var/etcd should have write permission for the current user.

Run master:
```
python master/master.py
```

Run minion:

```
python minon/daemon.py --master <master's_ip_address> --interface
<ethernet_interface_to_use>
```



