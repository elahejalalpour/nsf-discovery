import sys, os
sys.path.append(os.getcwd() + "/..")
from minion import container_driver

mon = container_driver.ContainerDriver("minion.mock_docker")

def test_get_containers():
	assert(mon.get_containers() != None)

def test_get_id():
	assert(mon.get_id('nfuser-new-firewall') == 'd998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331')
	
def test_get_container_pid():
	assert(mon.get_container_pid('nfuser-new-firewall') == 3790)
	
def test_get_ip():
	assert(mon.get_ip('nfuser-new-firewall') == '172.17.0.2')

def test_execute_in_guest():
    assert(mon.execute_in_guest('nfuser-new-firewall','ls') == None)
    
def test_guest_status():
    assert(mon.guest_status('nfuser-new-firewall') == 'running')
    
def test_start():
    mon.start('whatever')
    
def test_restart():
    mon.restart('whatever')

def test_stop():
    mon.stop('whatever')

def test_pause():
    mon.pause('whatever')
    
def test_unpause():
    mon.unpause('whatever')
    
def test_deploy():
    assert(mon.deploy('a','b','c') == '0000000000')
    
def test_destroy():
    mon.destroy('whatever')
    
def test_images():
    assert(mon.images() != None)
