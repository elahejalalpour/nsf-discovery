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
        bash_command = "sudo ovs-ofctl -O add-flow " + \
            ovs_bridge_name + " " + rule
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
        bash_command = "sudo ovs-ofctl -O del-flow " + \
            ovs_bridge_name + " " + rule
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    @staticmethod
    def attach_interface_to_ovs(ovs_bridge_name, veth_interface_name):
        """
        Attaches a veth interface to an OVS bridge.

        @param ovs_bridge_name Name of the OVS bridge.
        @param veth_interface_name Name of the veth interface to attach
        """
        bash_command = "sudo ovs-vsctl add-port " + \
            ovs_bridge_name + " " + veth_interface_name
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    def detach_interface_from_ovs(ovs_bridge_name, veth_interface_name):
        """
        Remove a veth interface from an OVS bridge.

        @param ovs_bridge_name Name of the OVS bridge.
        @param veth_interface_name Name of the veth interface to dettach
        """
        bash_command = "sudo ovs-vsctl del-port " + \
            ovs_bridge_name + " " + veth_interface_name
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
        bash_command = "sudo ovs-vsctl list-ports " + \
            ovs_bridge_name + " | grep -c " + veth_interface_name
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)
        return int(output) > 0 ? True:
            False

    @staticmethod
    def get_openflow_port_number(ovs_bridge_name, veth_interface_name):
        """
        Returns the OpenFlow port identifier of the veth interface.

        @param ovs_bridge_name Name of the OVS bridge where the veth interface
        is connected.
        @param veth_interface_name Name of the veth interface whose port number
        is being queried

        @returns The OpenFlow port identifier of the veth interface if the
        interface is found on the bridge, -1 otherwise.
        """
        bash_command = "sudo ovs-ofctl -O OpenFlow13 dump-ports-desc " + \
            ovs_bridge_name + " | grep -o '.*(" + veth_interface_name + "):'" +\
            " | sed 's/\s\([0-9]*\).*/\\1/'"
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)
        if len(output) <= 0:
            return "-1"
        return output.strip()
