import logging
from bash_wrapper import execute_bash_command
from ovs_driver import OVSDriver
from veth_driver import VethDriver
from container_driver import ContainerDriver

logger = logging.getLogger(__name__)


class ChainDriver():

    def __init__(self):
        self.__container_handler = ContainerDriver()
    
    def connect_containers_inside_host(self, container_a_name,
            veth_vs_container_a, container_b_name, veth_vs_container_b,
            link_id, chain_rollback):
        """
        Connects two containers within the same physical hosts by a
        bi-directional link.

        @param container_a_name Name of one of the containers in the pair
        @param veth_vs_container_a Loose end of container a's veth pair link
        @param container_b_name Name of the other container in the pair
        @param veth_vs_container_b Loos end of container_b's veth pair link
        @param link_id Id of the link connecting container_a and container_b
        container_a and container_b
        @param chain_rollback Global rollback object
        """
        ovs_bridge_name = "ovs-br-" + str(link_id)
        OVSDriver.create_bridge(ovs_bridge_name)
        chain_rollback.push(OVSDriver.delete_bridge, ovs_bridge_name)
        
        OVSDriver.attach_interface_to_ovs(ovs_bridge_name,
                veth_vs_container_a)
        chain_rollback.push(OVSDriver.detach_interface_from_ovs, ovs_bridge_name,
                veth_vs_container_a)
        VethDriver.enable_veth_interface(veth_vs_container_a)

        OVSDriver.attach_interface_to_ovs(ovs_bridge_name,
                veth_vs_container_b)
        chain_rollback.push(OVSDriver.detach_interface_from_ovs, ovs_bridge_name,
                veth_vs_container_b)
        VethDriver.enable_veth_interface(veth_vs_container_b)


    def connect_container_across_hosts(
            self,
            container_name,
            veth_cn_container,
            veth_vs_container,
            ovs_bridge_name,
            container_ip_net,
            remote_container_ip,
            tunnel_id,
            tunnel_interface_name,
            chain_rollback):
        """
        Connects two containers on different hosts thru GRE tunnel.

        (All arguments must be passed as strings)
        @param container_name Name of the docker container.
        @param veth_cn_container Name of the veth interface connected with
        the container.
        @param veth_vs_container Name of the veth interface connected with
        the ovs bridge.
        @param ovs_bridge_name The bridge used for tunneling
        @param container_ip_net IP and network prefix (e.g., 192.168.100.101/24)
        @param remote_container_ip IP of the container at the other end of the
        tunnel (e.g., 192.168.100.102) no net-prefic here.
        @param tunnel_id ID of the tunnel connecting this container to the other
        @param tunnel_interface_name Name of the tunneling interface on
        this host.
        @param chain_rollback The global rollback context.

        Assumption;
            1. GRE tunnels are pre-established
            2. OVS bridges are operation in secure failure mode
            3. The container 'container_name' is already deployed and is running
        """

        # attach veth_endpoint_a to ovs
        OVSDriver.attach_interface_to_ovs(ovs_bridge_name, veth_vs_container)
        chain_rollback.push(
            OVSDriver.detach_interface_from_ovs, ovs_bridge_name,
            veth_vs_container)

        VethDriver.enable_veth_interface(veth_vs_container)

        # find the openflow port for this container
        container_of_port = str(OVSDriver.get_openflow_port_number(
                                    ovs_bridge_name, veth_cn_container))

        tunnel_id = str(tunnel_id)
        tunnel_of_port = str(OVSDriver.get_openflow_port_number(ovs_bridge_name,
            tunnel_interface_name))
        container_ip = container_ip_net.split("/")[0]

        # install rule to forward regular traffic
        egress_forwarding_rule = "in_port=" + container_of_port + \
            ",actions=set_tunnel:" + tunnel_id + \
                ",output:" + tunnel_of_port
        OVSDriver.install_flow_rule(
                                ovs_bridge_name,
                                egress_forwarding_rule)
        chain_rollback.push(OVSDriver.remove_flow_rule, ovs_bridge_name,
                        egress_forwarding_rule)

        ingress_forwarding_rule = "in_port=" + tunnel_of_port + ",tun_id=" + \
                tunnel_id + ",actions=output:" + container_of_port
        OVSDriver.install_flow_rule(ovs_bridge_name, ingress_forwarding_rule)

        chain_rollback.push(OVSDriver.remove_flow_rule, ovs_bridge_name,
                ingress_forwarding_rule)

        # install rule to handle arp traffic
        egress_arp_rule = "in_port=" + container_of_port + ",arp,nw_dst='"\
            + remote_container_ip + "'" + \
                ",actions=set_tunnel:" + tunnel_id\
            + ",output:" + tunnel_of_port
        OVSDriver.install_flow_rule(ovs_bridge_name, egress_arp_rule)
        chain_rollback.push(OVSDriver.remove_flow_rule, ovs_bridge_name,
                egress_arp_rule)

        ingress_arp_rule = "in_port=" + tunnel_of_port + ",arp,nw_dst='" +\
                container_ip + "'" + ",tun_id=" + tunnel_id +\
                ",actions=output:" + container_of_port
        OVSDriver.install_flow_rule(ovs_bridge_name, ingress_arp_rule)
        chain_rollback.push(OVSDriver.remove_flow_rule, ovs_bridge_name,
                ingress_arp_rule)


