import sys
import os
sys.path.append(os.getcwd() + "/..")
from minion import container_driver

cdriver = container_driver.ContainerDriver("minion.mock_docker")

def test_get_containers():
    assert(cdriver.get_containers() != None)
    assert(len(cdriver.get_containers(True)) == 2)
    assert(len(cdriver.get_containers(False)) == 1)

def test_is_empty():
    assert(cdriver._is_empty("") == True)
    assert(cdriver._is_empty("not-empty") == False)
    assert(cdriver._is_empty("0") == False)

def test_get_id():
    assert(cdriver.get_id('nfuser-new-firewall') ==
           'd998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331')
    try:
        cdriver.get_id('whatever')
        assert(False)
    except Exception as ex:
        assert(True)

def test_get_container_pid():
    assert(cdriver.get_container_pid('nfuser-new-firewall') == 3790)
    assert(cdriver.get_container_pid('nfuser-edge-ufw-1') == 0)
    print cdriver.get_container_pid('nfuser-edge-ufw-1')
    try:
        cdriver.get_container_pid('whatever')
        assert(False)
    except Exception as ex:
        assert(True)

def test_get_ip():
    assert(cdriver.get_ip('nfuser-new-firewall') == '172.17.0.2')
    try:
        cdriver.get_ip('nfuser-edge-ufw-1')
        assert(False)
    except Exception as ex:
        assert(True)
    try:
        cdriver.get_ip('whatever')
        assert(False)
    except Exception as ex:
        assert(True)


def test_execute_in_guest():
    assert(cdriver.execute_in_guest('nfuser-new-firewall', 'ls') == None)


def test_guest_status():
    assert(cdriver.guest_status('nfuser-new-firewall') == 'running')
    assert(cdriver.guest_status('nfuser-edge-ufw-1') == 'exited')
    try:
        cdriver.guest_status('whatever')
        assert(False)
    except Exception as ex:
        assert(True)


def test_start():
    cdriver.start('d998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331')
    try:
        cdriver.start('000')
        assert(False)
    except Exception as ex:
        assert(True)
    try:
        cdriver.start('')
        assert(False)
    except Exception as ex:
        assert(True)


def test_restart():
    cdriver.restart('d998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331')
    try:
        cdriver.restart('000')
        assert(False)
    except Exception as ex:
        assert(True)


def test_stop():
    cdriver.stop('d998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331')
    try:
        cdriver.stop('000')
        assert(False)
    except Exception as ex:
        assert(True)


def test_pause():
    cdriver.pause('d998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331')
    try:
        cdriver.pasuse('000')
        assert(False)
    except Exception as ex:
        assert(True)


def test_unpause():
    cdriver.unpause('d998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331')
    try:
        cdriver.unpause('000')
        assert(False)
    except Exception as ex:
        assert(True)


def test_deploy():
    assert(cdriver.deploy('a', 'b', 'c') == '0000000000')
    try:
        cdriver.deploy('', 'b', 'c')
        assert(False)
    except Exception as ex:
        assert(True)

def test_destroy():
    cdriver.destroy('d998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331')
    try:
        cdriver.destroy('000')
        assert(False)
    except Exception as ex:
        assert(True)


def test_images():
    assert(cdriver.images() != None)
    
def test_unlink_container_netns():
    cdriver.unlink_container_netns('d998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331')
    
def test_symlink_container_netns():
    cdriver.symlink_container_netns('d998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331')
    
def test_get_container_net_ifaces():
    cdriver.get_container_net_ifaces('d998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331')
    
