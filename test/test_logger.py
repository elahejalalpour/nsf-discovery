import sys
import os
sys.path.append(os.getcwd() + "/..")
from master import logger

influx = logger.influxwrapper('master.mock_influx')

def test_clear():
    influx.clear()
    
def test_log_host():
    influx.log_host('nfio','10.0.0.1','event')
    
def test_log_cpu():
    influx.log_cpu('nfio',0.5)
    
def test_log_host():
    influx.log_mem('nfio',0.6)
    
def test_log_vnf():
    influx.log_vnf('abcd','firewall','nfio','event')
    
def test_log_chain():
    influx.log_chain('first-chain','event')
