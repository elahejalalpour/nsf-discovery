from container_driver import ContainerDriver
from bash_wrapper import execute_bash_command
import copy
from random import randint
from veth_driver import VethDriver
from ovs_driver import OVSDriver
from chain_driver import ChainDriver
from rollbackcontext import RollbackContext


class ProvisioningAgent():

    def __init__(self, ovs_bridge_name = "ovs-br0"):
        self.__container_handle = ContainerDriver()
        self.__default_ovs_bridge = ovs_bridge_name
        self.__chain_driver = ChainDriver()

    def provision_single_vnf(self, vnf_config, chain_rollback):
        # Deploy the container.
        self.__container_handle.deploy(
            user="sr2chowd",
            image_name=vnf_config['vnf_type'],
            vnf_name=vnf_config['container_name'])
        container_name = "sr2chowd-" + vnf_config['container_name']
        chain_rollback.push(self.__container_handle.destroy,
                self.__container_handle, container_name)

        # Start the container 
        self.__container_handle.start(vnf_name=container_name)
        chain_rollback.push(self.__container_handle.stop, self.__container_handle,
                container_name)

        # Retrieve container pid and create symlink to netns under
        # /var/run/netns
        cont_pid = str(self.__container_handle.get_container_pid(container_name))
        print "Container " + container_name + " started with pid " + cont_pid
        vnf_config["container_name"] = container_name
        self.__container_handle.symlink_container_netns(container_name)
        chain_rollback.push(self.__container_handle.symlink_container_netns,
                self.__container_handle, container_name)

        for net_config in vnf_config['net_ifs']:
            print net_config
            veth_vs, veth_cn = self.generate_unique_veth_endpoints(container_name,
                    self.__default_ovs_bridge)
            print "Creating veth pair (" + veth_cn + ", " + veth_vs + ")\n" 
            VethDriver.create_veth_pair(veth_cn, veth_vs)
            chain_rollback.push(VethDriver.delete_veth_interface, veth_cn)
            chain_rollback.push(VethDriver.delete_veth_interface, veth_vs)

            VethDriver.move_veth_interface_to_netns(veth_cn, netns = cont_pid)
            VethDriver.update_mtu_at_veth_interface(veth_cn, 1436, netns = cont_pid)
            VethDriver.enable_veth_interface(veth_cn, netns = cont_pid)

            VethDriver.assign_ip_to_veth_interface(veth_cn, net_config['ip_address'], netns =
                    cont_pid)
            chain_rollback.push(VethDriver.delete_ip_from_veth_interface,
                    net_config['ip_address'], netns = cont_pid)

            VethDriver.enable_veth_interface(veth_cn, netns = cont_pid)
            net_config["veth_cn"] = veth_cn
            net_config["veth_vs"] = veth_vs
        return vnf_config

    def provision_local_chain(self, chain_config):
        with RollbackContext() as chain_rollback:
            updated_chain_config = []
            for vnf_config in chain_config:
                print "####################"
                print vnf_config
                updated_chain_config.append(copy.deepcopy(
                        self.provision_single_vnf(vnf_config, chain_rollback)))
            
            # identify the links
            links = {}
            print updated_chain_config
            for vnf_conf in updated_chain_config:
                print vnf_config
                for net_conf in vnf_conf['net_ifs']:
                    print net_conf
                    link_id = net_conf['link_id']
                    if link_id not in links.keys():
                        links[link_id] = {"link_type" : net_conf["link_type"]}
                        links[link_id]["endpoint_a"] = vnf_conf["container_name"]
                        links[link_id]["veth_vs_a"] =  net_conf["veth_vs"]
                        links[link_id]["veth_cn_a"] =  net_conf["veth_cn"]
                    else:
                        links[link_id]["endpoint_b"] = vnf_conf["container_name"]
                        links[link_id]["veth_vs_b"] = net_conf["veth_vs"]
                        links[link_id]["veth_cn_b"] = net_conf["veth_cn"]

            for (link_id, link) in links.iteritems():
                print type(link)
                if link["link_type"] == "local":
                    a, b = link["endpoint_a"], link["endpoint_b"]
                    veth_vs_a = link["veth_vs_a"]
                    veth_vs_b = link["veth_vs_b"]
                    ovs_bridge_name = "ovs-br-" + str(link_id)
                    self.__chain_driver.connect_containers_inside_host(a["container_name"],
                            veth_vs_a, b["container_name"], veth_vs_a,
                            ovs_bridge_name, chain_rollback)
            chain_rollback.commitAll()

    def generate_unique_veth_endpoints(self, container_name, ovs_bridge_name):
        veth_endpoint_a = ""
        veth_endpoint_b = ""
        container_pid = str(self.__container_handle.get_container_pid(
            container_name))
        while(True):
            # generate a 4-digit random number
            veth_id = randint(100, 999)

            # build veth endpoint names
            veth_endpoint_a = "veth" + str(veth_id) + "-vs"
            veth_endpoint_b = "veth" + str(veth_id) + "-cn"

            present_in_host = VethDriver.is_interface_present(veth_endpoint_a)
            present_in_ovs = OVSDriver.is_interface_attached(ovs_bridge_name,
                                                             veth_endpoint_a)
            present_in_container = VethDriver.is_interface_present(veth_endpoint_b,
                                                                    netns=container_pid)

            if present_in_host or present_in_ovs or present_in_container:
                continue
            break
        return (veth_endpoint_a, veth_endpoint_b)
