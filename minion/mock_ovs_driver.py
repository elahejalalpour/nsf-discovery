class MockOVSDriver:

    def __init__(self):
        self._bridges = []
        self._ports = {}
        self._rules = {}
        # self.create_bridge("ovs0")
        # self.attach_interface_to_ovs("ovs0", "gre0")

    def get_bridges(self):
        return self._bridges

    def get_ports(self, bridge):
        return self._ports[bridge]

    def create_bridge(self, ovs_bridge_name):
        if ovs_bridge_name in self._bridges:
            return -1, "", "ovs-vsctl: cannot create a bridge named " +\
                    ovs_bridge_name + " because a bridge named " +\
                    ovs_bridge_name + " already exists"
        self._bridges.append(ovs_bridge_name)
        self._ports[ovs_bridge_name] = []
        self._rules[ovs_bridge_name] = []
        return 0, "", ""

    def delete_bridge(self, ovs_bridge_name):
        if ovs_bridge_name not in self._bridges:
            return -1, "", "ovs-vsctl: no bridge named " + ovs_bridge_name
        print self._bridges
        self._bridges.remove(ovs_bridge_name)
        if self._ports.has_key(ovs_bridge_name):
            del self._ports[ovs_bridge_name] 
        if self._rules.has_key(ovs_bridge_name):
            del self._rules[ovs_bridge_name]
        print self._bridges
        return 0, "", ""

    def set_bridge_of_version(self, ovs_bridge_name, of_version="OpenFlow13"):
        if ovs_bridge_name not in self._bridges:
            return -1, '', 'ovs-vsctl: no row "' + ovs_bridge_name + '" in table Bridge'
        return 0, "", ""

    def set_bridge_fail_mode(self, ovs_bridge_name, fail_mode="secure"):
        if ovs_bridge_name not in self._bridges:
            return -1, "", "ovs-vsctl: no bridge named " + ovs_bridge_name
        return 0, "", ""

    def install_flow_rule(self, ovs_bridge_name, rule):
        if ovs_bridge_name not in self._bridges:
            return -1, '', 'ovs-ofctl: ' + ovs_bridge_name + ' is not a bridge or a socket'
        self._rules[ovs_bridge_name].append(rule)
        return 0, "", ""

    def attach_interface_to_ovs(self, ovs_bridge_name, veth_interface_name):
        if ovs_bridge_name not in self._bridges:
            return -1, '', "ovs-vsctl: no bridge named " + ovs_bridge_name
        for bridge in self._bridges:
            if veth_interface_name in self._ports[bridge]:
                return -1, '', "ovs-vsctl: cannot create a port named " +\
                        veth_interface_name + " because a port named " +\
                        veth_interface_name + " already exists on bridge " +\
                        bridge
        self._ports[ovs_bridge_name].append(veth_interface_name)
        return 0, "", ""

    def detach_interface_from_ovs(self, ovs_bridge_name, veth_interface_name):
        if veth_interface_name == ovs_bridge_name:
            return -1, '', 'ovs-vsctl: cannot delete port ' +\
                    veth_interface_name + ' because it is the local port for'+\
                    " bridge " + veth_interface_name + \
                    " (deleting this port requires deleting the entire bridge)"
        if (not self._ports.has_key(ovs_bridge_name)) or (veth_interface_name not in self._ports[ovs_bridge_name]):
            return -1, "", "ovs-vsctl: no port named " + veth_interface_name
        self._ports[ovs_bridge_name].remove(veth_interface_name)
        return 0, "", ""

    def is_interface_attached(self, ovs_bridge_name, veth_interface_name):
        return 0, str(veth_interface_name in self._ports[ovs_bridge_name]), ""

    def get_openflow_port_number(self, ovs_bridge_name, veth_interface_name):
        return 0, str(self._ports[ovs_bridge_name].index(veth_interface_name)), ""

    def get_tunnel_port_number(self, ovs_bridge_name, veth_interface_name):
        return 0, str(self._ports[ovs_bridge_name].index(veth_interface_name)), ""
