import sys
import os
sys.path.append(os.getcwd() + "/../minion")
from minion import ovs_driver
from minion import resource_broker



def test_create_bridge():
    rb = resource_broker.ResourceBroker()
    rb.register_resource("BashWrapper", "mock_bash_wrapper")
    odriver = ovs_driver.OVSDriver(rb)
    odriver.create_bridge("ovs-0")
    odriver.create_bridge("ovs-1")
    assert(odriver.is_bridge_created("ovs-0") == True)
    assert(odriver.is_bridge_created("ovs-1") == True)
    try:
        odriver.create_bridge("ovs-0")
        assert(True == False)
    except Exception as ex:
        print ex[1]
        expected = "ovs-vsctl: cannot create a bridge named ovs-0 because a bridge named ovs-0 already exists"
        assert(ex[1] == expected)
    odriver.delete_bridge("ovs-0")
    odriver.delete_bridge("ovs-1")

def test_delete_bridge():
    rb = resource_broker.ResourceBroker()
    rb.register_resource("BashWrapper", "mock_bash_wrapper")
    odriver = ovs_driver.OVSDriver(rb)
    odriver.create_bridge("ovs-0")
    odriver.delete_bridge("ovs-0")
    assert(odriver.is_bridge_created("ovs-0") == False)
    try:
        odriver.delete_bridge("nonexistent")
        assert(True == False)
    except Exception as ex:
        assert(ex[1] == "ovs-vsctl: no bridge named nonexistent")


def test_attach_interface():
    rb = resource_broker.ResourceBroker()
    rb.register_resource("BashWrapper", "mock_bash_wrapper")
    odriver = ovs_driver.OVSDriver(rb)
    odriver.create_bridge("ovs-0")
    odriver.create_bridge("ovs-1")
    assert(odriver.is_bridge_created("ovs-0") == True)
    assert(odriver.is_bridge_created("ovs-1") == True)
    odriver.attach_interface_to_ovs("ovs-0", "port-0")
    assert(odriver.is_interface_attached("ovs-0", "port-0") == True)

    # Attach interface to a bridge that does not exist.
    try:
        odriver.attach_interface_to_ovs("nonexistent", "port-0")
        assert(True == False)
    except Exception as ex:
        expected = "ovs-vsctl: no bridge named nonexistent"
        assert(ex[1] == expected)
    
    # Attach a port that is already attached.
    try:
        odriver.attach_interface_to_ovs("ovs-0", "port-0")
        assert(True == False)
    except Exception as ex:
        expected = "ovs-vsctl: cannot create a port named port-0 because a port named port-0 already exists on bridge ovs-0"
        assert(ex[1] == expected)

    # Attach a port that is already attached to another bridge.
    try:
        odriver.attach_interface_to_ovs("ovs-1", "port-0")
        assert(True == False)
    except Exception as ex:
        expected = "ovs-vsctl: cannot create a port named port-0 because a port named port-0 already exists on bridge ovs-0"
        assert(ex[1] == expected)

    odriver.delete_bridge("ovs-0")
    odriver.delete_bridge("ovs-1")

def test_detach_interface():
    rb = resource_broker.ResourceBroker()
    rb.register_resource("BashWrapper", "mock_bash_wrapper")
    odriver = ovs_driver.OVSDriver(rb)
    odriver.create_bridge("ovs-0")
    assert(odriver.is_bridge_created("ovs-0") == True)
    odriver.attach_interface_to_ovs("ovs-0", "port-0")
    assert(odriver.is_interface_attached("ovs-0", "port-0") == True)
    odriver.detach_interface_from_ovs("ovs-0", "port-0")
    assert(odriver.is_interface_attached("ovs-0", "port-0") == False)
    # Detach an interface that does not exist.
    try:
        odriver.detach_interface_from_ovs("ovs-0", "port-0")
        assert(True == False)
    except Exception as ex:
        expected = "ovs-vsctl: no port named port-0"
        assert(ex[1] == expected)

    try:
        odriver.detach_interface_from_ovs("ovs-0", "ovs-0")
        assert(True == False)
    except Exception as ex:
        expected = "ovs-vsctl: cannot delete port ovs-0 because it is the local port for bridge ovs-0 (deleting this port requires deleting the entire bridge)"
        assert(ex[1] == expected)

    odriver.delete_bridge("ovs-0")

def get_openflow_port_number():
    rb = resource_broker.ResourceBroker()
    rb.register_resource("BashWrapper", "mock_bash_wrapper")
    odriver = ovs_driver.OVSDriver(rb)
    odriver.create_bridge("ovs-0")
    assert(odriver.is_bridge_created("ovs-0") == True)
    odriver.attach_interface_to_ovs("ovs-0", "port-0")
    assert(odriver.is_interface_attached("ovs-0", "port-0") == True)
    odriver.attach_interface_to_ovs("ovs-0", "port-1")
    assert(odriver.is_interface_attached("ovs-0", "port-1") == True)
    odriver.attach_interface_to_ovs("ovs-0", "port-2")
    assert(odriver.is_interface_attached("ovs-0", "port-2") == True)
    assert(odriver.get_openflow_port_number("ovs-0", "port-2") == 2)
    odriver.detach_interface_from_ovs("ovs-0", "port-1")
    assert(odriver.get_openflow_port_number("ovs-0", "port-2") == 2)
    assert(odriver.get_openflow_port_number("ovs-0", "port-3") == -1)
    odriver.delete_bridge("ovs-0")
