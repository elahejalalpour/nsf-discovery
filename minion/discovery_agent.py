class DiscoveryAgent():

    def __init__(self, resource_broker, tunnel_bridge_name = "ovs-br0"):
        self.__container_driver =\
            resource_broker.get_resource("ContainerDriver")
        self.__ovs_driver = resource_broker.get_resource("OVSDriver")
        self.__tunnel_bridge_name = tunnel_bridge_name

    def __get_ovs_veth_endpoint(self, container_veth_endpoint):
        return container_veth_endpoint[:-2] + 'vs'

    def discover(self):
        partial_view_dict = {}
        container_list = []
        ovs_bridges_and_ports = self.__ovs_driver.get_ovs_bridges_and_ports()
        #print ovs_bridges_and_ports

        containers = self.__container_driver.get_containers()
        for container in containers:
            container_dict = {}

            container_name = container[u'Names'][0][1:].encode('ascii')
            container_dict['container_id'] = container_name

            net_ifaces_list = []
            container_net_ifaces = \
                self.__container_driver.get_container_net_ifaces(
                container_name)
            for net_iface in container_net_ifaces:
                ovs_net_iface = self.__get_ovs_veth_endpoint(net_iface)
                net_iface_dict = {}
                net_iface_dict['if_name'] = net_iface
                for ovs_bridge in ovs_bridges_and_ports:
                    if ovs_bridge == self.__tunnel_bridge_name:
                        if ovs_net_iface in \
                            ovs_bridges_and_ports[ovs_bridge]:
                            net_iface_dict['link_type'] ='gre'
                        
                            net_iface_dict['link_id'] = \
                                self.__ovs_driver.get_tunnel_port_number(
                                    ovs_bridge, ovs_net_iface)
                    else:
                        if ovs_net_iface in \
                            ovs_bridges_and_ports[ovs_bridge]:
                            net_iface_dict['link_type'] ='internal'
                            net_iface_dict['link_id'] = ovs_bridge
                    
                net_ifaces_list.append(net_iface_dict)
            container_dict['net_ifs'] = net_ifaces_list
            container_list.append(container_dict)
        partial_view_dict['containers'] = container_list
        return partial_view_dict
