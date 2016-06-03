import requests

import logging
from contextlib import contextmanager

import docker

import errors

logger = logging.getLogger(__name__)

class Monitor():
    """
    @class Monitor

    This class provides methods for monitoring docker containers.
    """
      
    def __init__(self):
        """
        @brief Instantiates a Monitor object.

        """
        self.__dns_list = ['8.8.8.8']

    @contextmanager
    def _error_handling(self, nfioError):
        """
        @beief convert docker-py exceptions to nfio exceptions
        
        This code block is used to catch docker-py docker-py exceptions 
        (from error.py), log them, and then raise nfio related 
        exceptions. 

        @param nfioError A Exception type from nfio's errors module 
        """
        try:
            yield
        except Exception, ex:
            #logger.error(ex.message, exc_info=False)
            print(ex.message)
            raise nfioError

    def _is_empty(self, string):
        """
        @brief checks whether a string is empty or None
    
        @param string input string
      
        @returns True if string is empty, otherwise False
        """
        return string is None or string.strip() == ""

    def _validate_image_name(self, image_name):
        if self._is_empty(image_name):
            raise errors.VNFImageNameIsEmptyError
    
    def _validate_cont_name(self, cont_name):
        if self._is_empty(cont_name):
            raise errors.VNFNameIsEmptyError

    def _get_client(self):
        """
        Returns a Docker client.
        
        @return A docker client object that can be used to communicate 
            with the docker daemon on the host
        """
        with self._error_handling(errors.HypervisorConnectionError):
          return docker.Client(base_url='unix://var/run/docker.sock')

    def _lookup_vnf(self, vnf_name):
        self._validate_cont_name(vnf_name)
        dcx = self._get_client()
        with self._error_handling(errors.VNFNotFoundError):
            inspect_data = dcx.inspect_container(container=vnf_name)
            return dcx, vnf_name, inspect_data

    def get_containers(self):
        """
        Returns all container's INFO.
          
          @return information of all containers in a list.
        """
        dcx = self._get_client()
        return dcx.containers(all=True)

    def get_id(self, vnf_name):
        """
        Returns a container's ID.
        
          @param vnf_name name of the VNF instance whose ID is being queried
          
          @return docker container ID.
        """
        dcx, vnf_fullname, inspect_data = self._lookup_vnf(vnf_name)
        return inspect_data['Id'].encode('ascii')

    def get_ip(self, vnf_name):
        """
        Returns a container's IP address.
        
          @param vnf_name name of the VNF instance whose ID is being queried
          
          @return docker container's IP.
        """
        if self.guest_status( vnf_name) != 'running':
            raise errors.VNFNotRunningError
        dcx, vnf_fullname, inspect_data = self._lookup_vnf(vnf_name)
        return inspect_data['NetworkSettings']['IPAddress'].encode('ascii')

    def execute_in_guest(self, vnf_name, cmd):
        """
        Executed commands inside a docker container.

        @param vnf_name name of the VNF
        @param cmd the command to execute inside the container

        @returns The output of the command passes as cmd
        """
        dcx, vnf_fullname, inspect_data = self._lookup_vnf(vnf_name)
        if self.guest_status(vnf_name) != 'running':
            raise errors.VNFNotRunningError
        with self._error_handling(errors.VNFCommandExecutionError):
            response = dcx.execute(vnf_fullname, 
                ["/bin/bash", "-c", cmd], stdout=True, stderr=False)
            return response

    def guest_status(self, vnf_name):
        """
        Returns the status of a docker container.

        @param user name of the user
        @param vnf_name name of the VNF

        @returns current state of the docker container
        """
        dcx, vnf_fullname, inspect_data = self._lookup_vnf(vnf_name)
        return inspect_data['State']['Status'].encode('ascii')
    def start(self, vnf_name, is_privileged=True):
        """
        Starts a docker container.

        @param vnf_name name of the VNF
        @param is_privileged if True then the container is started in 
            privileged mode
        """
        dcx, vnf_fullname, inspect_data = self._lookup_vnf(vnf_name)
        with self._error_handling(errors.VNFStartError):
            dcx.start(container=vnf_fullname,
                dns=self.__dns_list,
                privileged=is_privileged)

    def restart(self, vnf_name):
        """
        Restarts a docker container.

        @param user name of the user
        @param vnf_name name of the VNF
        """
        dcx, vnf_fullname, inspect_data = self._lookup_vnf(vnf_name)
        with self._error_handling(errors.VNFRestartError):
            dcx.restart(container=vnf_fullname)

    def stop(self, vnf_name):
        """
        Stops a docker container.

        @param user name of the user
        @param vnf_name name of the VNF
        """
        dcx, vnf_fullname, inspect_data = self._lookup_vnf(vnf_name)
        with self._error_handling(errors.VNFStopError):
            dcx.stop(container=vnf_fullname)

    def pause(self,vnf_name):
        """
        Pauses a docker container.

        @param user name of the user
        @param vnf_name name of the VNF
        """
        dcx, vnf_fullname, inspect_data = self._lookup_vnf(vnf_name)
        with self._error_handling(errors.VNFPauseError):
            dcx.pause(container=vnf_fullname)

    def unpause(self,vnf_name):
        """Unpauses a docker container.

        @param user name of the user
        @param vnf_name name of the VNF
        """
        dcx, vnf_fullname, inspect_data = self._lookup_vnf(vnf_name)
        with self._error_handling(errors.VNFUnpauseError):
            dcx.unpause(container=vnf_fullname)
            
    def deploy(self,user,image_name, vnf_name, is_privileged=True):
        """
        Deploys a docker container.

        
        @param user name of the user who owns the VNF
        @param image_name docker image name for the VNF
        @param vnf_name name of the VNF instance
        @param is_privileged if True then the container is deployed in 
            privileged mode

        @returns docker container ID
        """
        self._validate_image_name(image_name)
        vnf_fullname = user + '-' + vnf_name
        self._validate_cont_name(vnf_fullname)
        dcx = self._get_client()
        host_config = dict()
        if is_privileged:
            host_config['Privileged'] = True
        with self._error_handling(errors.VNFDeployError):
            container = dcx.create_container(
                image=image_name,
                name=vnf_fullname,
                host_config=host_config)
            return container['Id']

    def destroy(self, vnf_name, force=True):
        """
        Destroys a docker container.

        @param host IP address or hostname of the machine/VM where 
              the docker container is deployed
        @param user name of the user
        @param vnf_name name of the VNF
        @param force if set to False then a running VNF will not 
              be destroyed. default is True
        """
        dcx, vnf_fullname, inspect_data = self._lookup_vnf(vnf_name)
        with self._error_handling(errors.VNFDestroyError):
            dcx.remove_container(container=vnf_fullname, force=force)
