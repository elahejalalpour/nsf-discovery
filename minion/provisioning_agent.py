from resource_broker import ResourceBroker
import copy
from random import randint
from rollbackcontext import RollbackContext


class ProvisioningAgent():

    def __init__(self, resource_broker, ovs_bridge_name = "ovs-br0", 
                 tunnel_interface_name = "gre0"):
        self.__container_driver =\
            resource_broker.get_resource("ContainerDriver")
        self.__ovs_driver = resource_broker.get_resource("OVSDriver")
        self.__veth_driver = resource_broker.get_resource("VethDriver")
        self.__chain_driver = resource_broker.get_resource("ChainDriver")
        self.__default_ovs_bridge = ovs_bridge_name
        self.__default_tunnel_interface = tunnel_interface_name

    def provision_single_vnf(self, vnf_config, chain_rollback):
        """
        Deploys the container and creates the veth pairs for a single VNF. Only
        one end of the veth pairs are connected to the connected and the other
        end is left for the chaining driver to configure.

        @param vnf_config Configuraion dictionary for the VNF.
        @param chain_rollback Global rollback context.
        @returns An updated configuration. The updated configuration contains
        information about the added veth pairs and deployed container name.
        """
        # Deploy the container.
        scaled_cpu_share = int(1024 * (vnf_config['cpu_share'] / 100.0))
        host_config = {'Privileged': True}
        vnf_config_keys = vnf_config.keys()
        if "memory" in vnf_config_keys:
            host_config['mem_limit'] = str(vnf_config['memory']) + "M"
        if "cpu_share" in vnf_config_keys:
            host_config['CpuShares'] = int(1024 * (float(vnf_config['cpu_share']) / 100.0))
        if "cpuset_cpus" in vnf_config_keys:
            host_config['CpusetCpus'] = str(vnf_config['cpuset_cpus'])

        self.__container_driver.deploy(
            image_name=vnf_config['vnf_type'],
            vnf_name=vnf_config['container_name'],
            host_config = host_config)
        container_name = "sr2chowd-" + vnf_config['container_name']
        chain_rollback.push(self.__container_driver.destroy,
                self.__container_driver, container_name)

        # Start the container 
        self.__container_driver.start(vnf_name=container_name)
        chain_rollback.push(self.__container_driver.stop, self.__container_driver,
                container_name)

        # Retrieve container pid and create symlink to netns under
        # /var/run/netns
        cont_pid = str(self.__container_driver.get_container_pid(container_name))
        # print "Container " + container_name + " started with pid " + cont_pid
        vnf_config["container_name"] = container_name
        self.__container_driver.symlink_container_netns(container_name)
        chain_rollback.push(self.__container_driver.symlink_container_netns,
                self.__container_driver, container_name)

        
        # Create necessary veth pairs and attach them to the containers.
        for net_config in vnf_config['net_ifs']:
            veth_vs, veth_cn = self.generate_unique_veth_endpoints(container_name,
                    self.__default_ovs_bridge)
            # print "Creating veth pair (" + veth_cn + ", " + veth_vs + ")\n" 
            self.__veth_driver.create_veth_pair(veth_cn, veth_vs)
            chain_rollback.push(self.__veth_driver.delete_veth_interface, veth_cn)
            chain_rollback.push(self.__veth_driver.delete_veth_interface, veth_vs)

            self.__veth_driver.move_veth_interface_to_netns(veth_cn, netns = cont_pid)
            self.__veth_driver.update_mtu_at_veth_interface(veth_cn, 1436, netns = cont_pid)
            self.__veth_driver.enable_veth_interface(veth_cn, netns = cont_pid)

            self.__veth_driver.assign_ip_to_veth_interface(veth_cn, net_config['ip_address'], netns =
                    cont_pid)
            chain_rollback.push(self.__veth_driver.delete_ip_from_veth_interface,
                    net_config['ip_address'], netns = cont_pid)

            self.__veth_driver.enable_veth_interface(veth_cn, netns = cont_pid)
            net_config["veth_cn"] = veth_cn
            net_config["veth_vs"] = veth_vs

        return vnf_config

    def provision_local_chain(self, chain_config):
        """
        Create this host's local view of the chain. 
        
        @param chain_config Configuration dictionary for the chain.
        """
        with RollbackContext() as chain_rollback:
            updated_chain_config = []

            # First provision individual VNFs.
            for vnf_config in chain_config:
                updated_chain_config.append(copy.deepcopy(
                        self.provision_single_vnf(vnf_config, chain_rollback)))
            
            # Identify the links.
            links = {}
            # print updated_chain_config
            for i in range(0, len(updated_chain_config)):
                vnf_conf = updated_chain_config[i]
                for j in range(0, len(vnf_conf['net_ifs'])):
                    net_conf = vnf_conf['net_ifs'][j]
                    link_id = net_conf['link_id']
                    if link_id not in links.keys():
                        links[link_id] = {"link_type" : net_conf["link_type"]}
                        links[link_id]["endpoint_a"] = vnf_conf["container_name"]
                        links[link_id]["veth_vs_a"] =  net_conf["veth_vs"]
                        links[link_id]["veth_cn_a"] =  net_conf["veth_cn"]
                        links[link_id]["a_ip_address"] = net_conf["ip_address"]
                        links[link_id]["bandwidth"] = net_conf["bandwidth"]
                        if net_conf["link_type"] <> "local":
                            links[link_id]["remote_container_ip"] =\
                                net_conf["remote_container_ip"]
                    else:
                        links[link_id]["endpoint_b"] = vnf_conf["container_name"]
                        links[link_id]["veth_vs_b"] = net_conf["veth_vs"]
                        links[link_id]["veth_cn_b"] = net_conf["veth_cn"]
                        links[link_id]["b_ip_address"] = net_conf["ip_address"]

            # Once the links are identified, provision them by invoking the
            # chain driver.
            for (link_id, link) in links.iteritems():
                if link["link_type"] == "local":
                    a, b = link["endpoint_a"], link["endpoint_b"]
                    veth_vs_a = link["veth_vs_a"]
                    veth_vs_b = link["veth_vs_b"]
                    bandwidth = link["bandwidth"]
                    self.__chain_driver.connect_containers_inside_host(a,
                            veth_vs_a, b, veth_vs_b, link_id, bandwidth, chain_rollback)
                else:
                    a = link["endpoint_a"]
                    veth_vs = link["veth_vs_a"]
                    ovs_bridge_name = self.__default_ovs_bridge
                    container_ip_net = link["a_ip_address"]
                    remote_container_ip = link["remote_container_ip"].split("/")[0]
                    bandwidth = link["bandwidth"]
                    tunnel_id = str(link_id)
                    tunnel_interface_name = self.__default_tunnel_interface
                    self.__chain_driver.connect_containers_across_hosts(a,
                            veth_vs, ovs_bridge_name, container_ip_net,
                            remote_container_ip, tunnel_id,
                            tunnel_interface_name, bandwidth, chain_rollback)

            chain_rollback.commitAll()

    def generate_unique_veth_endpoints(self, container_name, ovs_bridge_name):
        """
        Generate a veth pair with unique names for its end points.

        @param container_name Name of the container that is going to attach to
        one veth interface.
        @param ovs_bridge_name Name of the ovs bridge where the other veth
        interface is going to attach.
        @returns A tuple representing the name of a veth pair.
        """
        veth_endpoint_a = ""
        veth_endpoint_b = ""
        container_pid = str(self.__container_driver.get_container_pid(
            container_name))
        while(True):
            # generate a 4-digit random number
            veth_id = randint(100, 999)

            # build veth endpoint names
            veth_endpoint_a = "veth" + str(veth_id) + "-vs"
            veth_endpoint_b = "veth" + str(veth_id) + "-cn"

            present_in_host = self.__veth_driver.is_interface_present(veth_endpoint_a)
            present_in_ovs = self.__ovs_driver.is_interface_attached(ovs_bridge_name,
                                                             veth_endpoint_a)
            present_in_container = self.__veth_driver.is_interface_present(veth_endpoint_b,
                                                                    netns=container_pid)

            if present_in_host or present_in_ovs or present_in_container:
                continue
            break
        return (veth_endpoint_a, veth_endpoint_b)
