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

def test_get_container_pid():
    assert(cdriver.get_container_pid('nfuser-new-firewall') == 3790)


def test_get_ip():
    assert(cdriver.get_ip('nfuser-new-firewall') == '172.17.0.2')


def test_execute_in_guest():
    assert(cdriver.execute_in_guest('nfuser-new-firewall', 'ls') == None)


def test_guest_status():
    assert(cdriver.guest_status('nfuser-new-firewall') == 'running')


def test_start():
    cdriver.start('whatever')


def test_restart():
    cdriver.restart('whatever')


def test_stop():
    cdriver.stop('whatever')


def test_pause():
    cdriver.pause('whatever')


def test_unpause():
    cdriver.unpause('whatever')


def test_deploy():
    assert(cdriver.deploy('a', 'b', 'c') == '0000000000')


def test_destroy():
    cdriver.destroy('whatever')


def test_images():
    assert(cdriver.images() != None)
