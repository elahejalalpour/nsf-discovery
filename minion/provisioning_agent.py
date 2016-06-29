from container_driver import ContainerDriver
from bash_wrapper import execute_bash_command


class ProvisioningAgent():

    def __init__(self, ovs_bridge_name = "ovs-br0"):
        self.__container_handle = ContainerDriver()
        self.__default_ovs_bridge = ovs_bridge_name

    def provision_single_vnf(self, vnf_config):
        #memory = vnf_config['memory']
        #cpu_share = vnf_config['cpu_share']
        #cpuset_cpus = vnf_config['cpuset_cpus']
        #container_name = vnf_config['container_name']
        #vnf_image = vnf_config['vnf_type']
        #print "c_name = " + container_name + ", image = " + vnf_image
        #ip_address = vnf_config['ip_address']

        self.__container_handle.deploy(
            user="sr2chowd",
            image_name=vnf_config['vnf_type'],
            vnf_name=vnf_config['container_name'])
        container_name = "sr2chowd-" + vnf_config['container_name']
        self.__container_handle.start(vnf_name=container_name)

        cont_pid = str(self.__container_handle.get_container_pid(container_name))
        print "Container " + container_name + " started with pid " + cont_pid
        #self.__container_handler.symlink_container_netns(container_name)
        #veth_cn, veth_vs = self.generate_unique_veth_endpoints(container_name,
        #        self.__default_ovs_bridge)
       
        #VethDriver.create_veth_pair(veth_cn, veth_vs)
        #VethDriver.move_veth_interface_to_netns(veth_cn, netns = cont_pid)
        #VethDriver.update_mtu_at_veth_interface(veth_cn, 1436, netns = cont_pid)
        #VethDriver.enable_veth_interface(veth_cn, netns = cont_pid)
        #VethDriver.assign_ip_to_veth_interface(veth_cn, ip_address, netns =
        #        cont_pid)
        #VethDriver.enable_veth_interface(veth_cn, netns = cont_pid)


    def provision_local_chain(self, chain_config):
        for vnf_config in chain_config:
            print "####################"
            print vnf_config
            self.provision_single_vnf(vnf_config)

    def generate_unique_veth_endpoints(container_name, ovs_bridge_name):
        veth_endpoint_a = ""
        veth_endpoint_b = ""
        container_pid = self.__container_handle.get_container_pid(
            container_name)
        while(True):
            # generate a 4-digit random number
            veth_id = randint(100, 999)

            # build veth endpoint names
            veth_endpoint_a = "veth" + str(veth_id) + "-vs"
            veth_endpoint_b = "veth" + str(veth_id) + "-cn"

            present_in_host = VethDriver.is_interface_attached(veth_endpoint_a)
            present_in_ovs = OVSDriver.is_interface_attached(ovs_bridge_name,
                                                             veth_endpoint_a)
            present_in_container = VethDriver.is_interface_attached(veth_endpoint_b,
                                                                    netns=container_pid)

            if present_in_host or present_in_ovs or present_in_container:
                continue
            break
        return (veth_endpoint_a, veth_endpoint_b)
