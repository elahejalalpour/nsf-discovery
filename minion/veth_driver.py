import logging
import os
from bash_wrapper import execute_bash_command
import errors

logger = logging.getLogger(__name__)

class VethDriver():      
    @staticmethod
    def create_veth_pair(veth_interface_a, veth_interface_b):
        """
        Creates a link using veth pair.
    
        @param veth_interface_a One endpoint of the veth pair
        @param veth_interface_b Other endpoint of the veth pair
        """
        bash_command = "sudo ip link add " + veth_interface_a + " mtu 1500 type " + \
            " veth peer name " + veth_interface_b  + " mtu 1500"
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    @staticmethod
    def delete_veth_interface(veth_interface):
        """
        Deletes an endpoint of a veth pair.

        @param veth_interface Name of the virtual ethernet (veth) interface to delete
        """
        bash_command = "sudo ip link del " + veth_interface
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)


    @staticmethod
    def move_veth_interface_to_netns(veth_interface, netns):
        """
        Moves a veth interface inside a network namespace.

        @param veth_interface Name of the veth interface to move.
        @param netns Destination network namespace for the veth interface. A
        process's pid is used to identify its netns.
        """
        bash_command = "sudo ip link set " + veth_interface + " netns " + netns
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    @staticmethod
    def enable_veth_interface(veth_interface, netns = "root"):
        """
        Brings up a veth interface inside a network namespace.

        @param veth_interface Name of the veth interface to enable.
        @param netns Destination network namespace. root represents the global
        or root network namespace and not any specific process's namespace. A
        process's namespace is identified by it's pid.

        """
        bash_command = "sudo "
        if netns <> "root":
            bash_command += "ip netns exec " + netns + " "
        bash_command += "ip link set " + veth_interface + " up"
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    @staticmethod
    def assign_ip_to_veth_interface(veth_interface, ip, netns = "root"):
        """
        Assigns IP address to veth interface inside a network namespace.

        @param veth_interface Name of the veth interface to assign IP
        @param ip The IP address to assign
        @param netns Destination network namespace. root represents the global
        or root network namespace and not any specific process's namespace. A
        process's namespace is identified by it's pid.

        """
        bash_command = "sudo "
        if netns <> "root":
            bash_command += "ip netns exec " + netns + " "
        bash_command += " ip addr add " + ip + " dev " + veth_interface
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    @staticmethod
    def delete_ip_from_veth_interface(veth_interface, ip, netns = "root"):
        """
        Delete an IP address from a veth interface inside a network namespace. 

        @param veth_interface Name of the veth interface to delete IP address
        from.
        @param ip The IP address to delete.
        @param netns Destination network namespace. root represents the global
        or root network namespace and not any specific process's namespace. A
        process's namespace is identified by it's pid.

        """
        bash_command = "sudo "
        if netns <> "root":
            bash_command += "ip netns exec " + netns + " "
        bash_command += "ip addr del " + ip + " dev " + veth_interface
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    @staticmethod
    def add_route_to_veth_interface(veth_interface, network, netns = "root"):
        """
        Add a network route going through a veth interface inside a network
        namespace. 

        @param veth_interface Name of the veth interface.
        @param network Network address for the route.
        @param netns Destination network namespace. root represents the global
        or root network namespace and not any specific process's namespace. A
        process's namespace is identified by it's pid.

        """
        bash_command = "sudo "
        if netns <> "root":
            bash_command += "ip netns exec " + netns + " " 
        bash_command += "ip route add " + network + " dev " + veth_interface
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    @staticmethod
    def delete_route_from_veth_interface(veth_interface, network, netns = "root"):
        """
        Delete a network route going through a veth interface inside a network
        namespace. 

        @param veth_interface Name of the veth interface.
        @param network Network address for the route.
        @param netns Destination network namespace. root represents the global
        or root network namespace and not any specific process's namespace. A
        process's namespace is identified by it's pid.

        """
        bash_command = "sudo "
        if netns <> "root":
            bash_command += "ip netns exec " + netns + " "
        bash_command += "ip route del " + network + " dev " + veth_interface
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    @staticmethod
    def update_mtu_at_veth_interface(veth_interface, mtu, netns = "root"):
        """
        Update Maximum Transport Unit (MTU) of a veth interface inside a network
        namespace.

        @param veth_interface Name of the veth interface.
        @param mtu MTU to be set.
        @param netns Destination network namespace. root represents the global
        or root network namespace and not any specific process's namespace. A
        process's namespace is identified by it's pid.

        """
        bash_command = "sudo "
        if netns <> "root":
            bash_command += "ip netns exec " + netns + " "
        bash_command += "ip link set dev " + veth_interface + " mtu " + str(mtu)
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)

    @staticmethod
    def is_interface_present(veth_interface, netns = "root"):
        bash_command = "sudo "
        if netns <> "root":
            bash_command += "ip netns exec " + netns + " "
        bash_command += "ip link | grep -c " + veth_interface
        (return_code, output, errput) = execute_bash_command(bash_command)
        if return_code <> 0:
            raise Exception(return_code, errput)
        return int(output) > 0

