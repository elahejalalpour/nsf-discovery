from container_driver import ContainerDriver

class ProvisioningAgent():
    def __init__(self):
        self.__container_handle = ContainerDriver()

    def provision_single_vnf(self, vnf_config):
        memory = vnf_config['memory']
        cpu_share = vnf_config['cpu_share']
        cpuset_cpus = vnf_config['cpuset_cpus']
        container_name = vnf_config['container_name']
        vnf_image = vnf_config['vnf_type']

        self.__container_handle.deploy(user = "sr2chowd", image_name =
                vnf_image, vnf_name = container_name)


    def provision_local_chain(self, chain_config):
        for vnf_config in chain_config:
            self.provision_single_vnf(vnf_config)
        
