class MockOVSDriver:

    def __init__(self):
        self._bridges = []
        self._ports = {}
        self._rules = {}
        self.create_bridge("ovs0")
        self.attach_interface_to_ovs("ovs0", "gre0")

    def create_bridge(self, ovs_bridge_name):
        if ovs_bridge_name in self._bridges:
            raise Exception(-
                            1, "Bridge " +
                            ovs_bridge_name +
                            " already exists.")
        self.i_bridges.append(ovs_bridge_name)

    def delete_bridge(self, ovs_bridge_name):
        if ovs_bridge_name not in self._bridges:
            raise Exception(-
                            1, "Bridge " +
                            ovs_bridge_name +
                            " does not exist.")
        self._bridges.remove(ovs_bridge_name)

    def set_bridge_of_version(self, ovs_bridge_name, of_version="OpenFlow13"):
        if ovs_bridge_name not in self._bridges:
            raise Exception(-
                            1, "Bridge " +
                            ovs_bridge_name +
                            " does not exist.")

    def set_bridge_fail_mode(self, ovs_bridge_name, fail_mode="secure"):
        if ovs_bridge_name not in self._bridges:
            raise Exception(-
                            1, "Bridge " +
                            ovs_bridge_name +
                            " does not exist.")

    def install_flow_rule(self, ovs_bridge_name, rule):
        if ovs_bridge_name not in self._bridges:
            raise Exception(-
                            1, "Bridge " +
                            ovs_bridge_name +
                            " does not exist.")
        if ovs_bridge_name not in self._rules.keys():
            self._rules[ovs_bridge_name] = []
        self._rules[ovs_bridge_name].append(rule)

    def attach_interface_to_ovs(self, ovs_bridge_name, veth_interface_name):
        if ovs_bridge_name not in self._bridges:
            raise Exception(-
                            1, "Bridge " +
                            ovs_bridge_name +
                            " does not exist.")
        if ovs_bridge_name not in self._ports.keys():
            self._ports[ovs_bridge_name] = []
        self._ports[ovs_bridge_name].append(veth_interface_name)

    def detach_interface_from_ovs(self, ovs_bridge_name, veth_interface_name):
        if ovs_bridge_name not in self._bridges:
            raise Exception(-
                            1, "Bridge " +
                            ovs_bridge_name +
                            " does not exist.")
        self._ports[ovs_bridge_name].remove(veth_interface_name)

    def is_interface_attached(self, ovs_bridge_name, veth_interface_name):
        return veth_interface_name in self._ports[ovs_bridge_name]

    def get_openflow_port_number(self, ovs_bridge_name, veth_interface_name):
        return self._ports[ovs_bridge_name].index(veth_interface_name)

    def get_tunnel_port_number(self, ovs_bridge_name, veth_interface_name):
        return 0

    def get_ovs_bridges_and_ports(self):
        return self._ports
