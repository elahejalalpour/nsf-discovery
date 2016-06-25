import logging
from bash_wrapper import execute_bash_command
from ovs_driver import OVSDriver
from veth_driver import VethDriver
from minion import Minion

logger = logging.getLogger(__name__)


class ChainDriver():

    def __init__(self):
        self.__minion_handler = Minion()
    
    def connect_container_across_hosts(
            self,
            container_name,
            ovs_bridge_name,
            container_ip_net,
            tunnel_id,
            tunnel_of_port,
            remote_container_ip):
        """Connects two containers on different hosts thru GRE tunnel.

        Arguments: (All arguments must be passed as strings)
            container_name: name of the docker container
            ovs_bridge_name: the bridge used for tunneling
            container_ip_net: IP and network prefix (e.g., 192.168.100.101/24)
            tunnel_id: ID of the tunnel connecting this container to the other
            tunnel_of_port: OpenFlow port number where the tunnel to the other
              host is connected
            remote_container_ip: IP of the container at the other end of the
            tunnel (e.g., 192.168.100.102) no net-prefic here.

        Assumption;
            1. GRE tunnels are pre-established
            2. OVS bridges are operation in secure failure mode
            3. The container 'container_name' is already deployed and is running
         """

        with RollbackContext() as rollback:

            # get container pid
            nid = self.__minion_handler.get_container_pid(container_name)

            # symlink docker netspace
            self.__minion_handler.symlink_container_netspace(nid)

            # create veth pair
            #(veth_endpoint_a, veth_endpoint_b) = \
            #    generate_unique_veth_endpoints(
            #    container_name,
            #    ovs_bridge_name)
            VethDriver.create_veth_pair(veth_endpoint_a, veth_endpoint_b)
            rollback.push(VethDriver.delete_veth_endpoint, veth_endpoint_a)
            rollback.push(VethDriver.delete_veth_endpoint, veth_endpoint_b)

            # attach veth_endpoint_a to ovs
            OVSDriver.attach_interface_to_ovs(ovs_bridge_name, veth_endpoint_a)
            rollback.push(
                OVSDriver.detach_interface_from_ovs, ovs_bridge_name,
                veth_endpoint_a)

            # attach veth_endpoint_b to container
            VethDriver.move_veth_interface_to_netns(veth_endpoint_b, nid)

            # update mtu for container veth endpoint to account for tunneling
            # overhead.
            VethDriver.update_mtu_at_veth_interface(veth_endpoint_b, 1436, nid)

            # enable veth pair
            VethDriver.enable_veth_interface(veth_endpoint_a)
            VethDriver.enable_veth_interface(veth_endpoint_b, netns = str(nid))

            # assign ip address to veth_endpoint_b
            VethDriver.assign_ip_to_veth_interface(
                    veth_endpoint_b, container_ip_net, str(nid))
            rollback.push(VethDriver.delete_ip_from_veth_interface, veth_endpoint_b,
                          container_ip_net, str(nid))

            # enable veth pair (just a precaution)
            VethDriver.enable_veth_interface(veth_endpoint_a)
            VethDriver.enable_veth_interface(veth_endpoint_b, netns = str(nid))

            # find the openflow port for this container
            container_of_port = OVSDriver.get_openflow_port_number(ovs_bridge_name, veth_endpoint_a)
            
            tunnel_id = str(tunnel_id)
            tunnel_of_port = str(tunnel_of_port)
            container_ip = container_ip_net.split("\\")[0]

            # install rule to forward regular traffic
            egress_forwarding_rule = "in_port=" + container_of_port + 
                ",actions=set_tunnel:" + tunnel_id + ",output:" + tunnel_of_port
            OVSDriver.install_flow_rule(ovs_bridge_name, egress_forwarding_rule)
            rollback.push(OVSDriver.remove_flow_rule, ovs_bridge_name, egress_forwarding_rule)
            
            ingress_forwarding_rule = "in_port=" + tunnel_of_port + ",tun_id=" +
                    tunnel_id + ",actions=output:" + container_of_port
            OVSDriver.install_flow_rule(ovs_bridge_name,
                    ingress_forwarding_rule)

            rollback.push(OVSDriver.remove_flow_rule, ovs_bridge_name,
                    ingress_forwarding_rule)

            # install rule to handle arp traffic
            egress_arp_rule = "in_port=" + container_of_port + ",arp,nw_dst='" 
                + remote_container_ip + "'" + ",actions=set_tunnel:" + tunnel_id
                + ",output:" + tunnel_of_port
            OVSDriver.install_flow_rule(ovs_bridge_name, egress_arp_rule)
            rollback.push(OVSDriver.remove_flow_rule, ovs_bridge_name,
                    egress_arp_rule)

            ingress_arp_rule = "in_port=" + tunnel_of_port + ",arp,nw_dst='" +
                    container_ip + "'" + ",tun_id=" + tunnel_id + 
                    ",actions=output:" + container_of_port)
            OVSDriver.install_flow_rule(ovs_bridge_name, ingress_arp_rule)
            rollback.push(OVSDriver.remove_flow_rule, ovs_bridge_name,
                    ingress_arp_rule)

            # All operations successfull, so commit them all!
            rollback.commitAll()
