import logging
from bash_wrapper import execute_bash_command

logger = logging.getLogger(__name__)

class OVSDriver():
    @staticmethod
    def install_flow_rule(ovs_bridge_name, rule):
        """
        Install an Openflow rule in the OVS bridge
        @param ovs_bridge_name Name of the OVS bridge.
        @param rule The Openflow rule to install.
        """
        bash_command = "sudo ovs-ofctl -O add-flow " + ovs_bridge_name + " " + rule
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    @staticmethod
    def remove_flow_rule(ovs_bridge_name, rule):
        """
        Remove a flow rule from an OVS bridge.
        @param ovs_bridge_name Name of the OVS bridge.
        @param rule The rule to remove.
        """
        bash_command = "sudo ovs-ofctl -O del-flow " + ovs_bridge_name + " " + rule
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)
    
    @staticmethod
    def is_interface_attached(ovs_bridge_name, veth_interface_name):
        """
        Checks if a virtual ethernet interface is attached to an OVS bridge.
        @param ovs_bridge_name Name of the OVS bridge.
        @param veth_interface_name Name of the veth interface to check.

        @returns True if veth_interface_name is attached to ovs_bridge_name,
        False otherwise.
        """
        bash_command = "sudo ovs-vsctl list-ports " + ovs_bridge_name + " | grep -c " + veth_interface_name
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)
        return int(output) > 0 ? True : False

