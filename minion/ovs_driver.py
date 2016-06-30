import logging
from bash_wrapper import execute_bash_command

logger = logging.getLogger(__name__)


class OVSDriver():

    @staticmethod
    def create_bridge(ovs_bridge_name):
        """
        Creates an OVS bridge

        @param ovs_bridge_name Name of the bridge to create.
        """
        bash_command = "sudo ovs-vsctl add-br " + ovs_bridge_name
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    @staticmethod
    def delete_bridge(ovs_bridge_name):
        """
        Delete an existing ovs bridge.
        
        @param ovs_bridge_name Name of the ovs bridge to delete.
        """
        bash_command = "sudo ovs-vsctl del-br " + ovs_bridge_name
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    @staticmethod
    def set_bridge_of_version(ovs_bridge_name, of_version = "OpenFlow13"):
        """
        Set the OpenFlow protocol version for an OVS bridge.

        @param ovs_bridge_name Name of the ovs bridge
        @param of_version OpenFlow Protocl Version (OpenFlow10, OpenFlow11,
        OpenFlow12, OpenFlow13 and so on). Default is OpenFlow13.
        """
        bash_command = "ovs-vsctl set bridge " + ovs_bridge_name + " protocols=" + of_version
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    @staticmethod
    def set_bridge_fail_mode(ovs_bridge_name, fail_mode = "secure"):
        """
        Sets the configured failure mode for the ovs bridge.

        @param ovs_bridge_name Name of the ovs bridge.
        @param fail_mode Failure mode for the bridge (standalone or secure).
        """
        bash_command = "ovs-vsctl set-fail-mode " + ovs_bridge_name + " " + fail_mode
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    @staticmethod
    def install_flow_rule(ovs_bridge_name, rule):
        """
        Install an Openflow rule in the OVS bridge
        @param ovs_bridge_name Name of the OVS bridge.
        @param rule The Openflow rule to install.
        """
        bash_command = "sudo ovs-ofctl -O OpenFlow13 add-flow " + \
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
        bash_command = "sudo ovs-ofctl -O OpenFlow13 del-flow " + \
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
        return True if int(output) > 0 else False

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

    @staticmethod
    def get_tunnel_port_number(ovs_bridge_name, veth_interface_name):
        veth_openflow_port = OVSDriver.get_openflow_port_number(ovs_bridge_name,
            veth_interface_name)
        if veth_openflow_port == '-1':
            return '-1'
        bash_command = "sudo ovs-ofctl -O OpenFlow13 dump-flows " + \
            ovs_bridge_name + " | grep -o in_port=" + veth_openflow_port + \
            ".*set_tunnel:[x0-9]* | grep -v arp | grep -o tunnel:[x0-9]* | " + \
            "sed 's/.*:\(.*\)/\\1/'"
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)
        try:
            tunnel_port = str(int(output.strip(), 16))
            return tunnel_port
        except:
            return '-1'

    @staticmethod
    def get_ovs_bridges_and_ports():

        bridges_and_ports = {}

        bash_command = 'sudo ovs-vsctl show | grep -o Bridge.*".*" ' + \
            ' | grep -o \\".*\\"'
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)
        output = output.replace('"', '')
        ovs_bridges = output.split()

        for ovs_bridge in ovs_bridges:
            bash_command = "sudo ovs-vsctl list-ports " + ovs_bridge
            (return_code, output, errput) = execute_bash_command(bash_command)
            if return_code <> 0:
                raise Exception(return_code, errput)
            ovs_ports = output.split()
            bridges_and_ports[ovs_bridge] = ovs_ports

        return bridges_and_ports

        
      




