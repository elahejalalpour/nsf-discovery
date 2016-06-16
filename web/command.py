import zmq

'''
	This class defines various types of commands
'''

class CMD():
	def __init__(self):
		self.__context = zmq.Context()
		self.__client = self.__context.socket(zmq.REQ)
		self.__client.connect('ipc:///tmp/test.pipe')
	def start(self,host,ID):
		"""
		Starts a docker container.
	  	@param host hostname of the VNF
	  	@param ID name or ID of the container
		"""
		msg = {'host' : host,'ID' : ID, 'action' : 'start'}
		self.__client.send_json(msg)
		self.__client.recv()
	def stop(self,host,ID):
		"""
		stops a docker container.
	  	@param host hostname of the VNF
	  	@param ID name or ID of the container
		"""
		msg = {'host' : host,'ID' : ID, 'action' : 'stop'}
		self.__client.send_json(msg)
		self.__client.recv()
	def restart(self,host,ID):
		"""
		restart a docker container.
	  	@param host hostname of the VNF
	  	@param ID name or ID of the container
		"""
		msg = {'host' : host,'ID' : ID, 'action' : 'restart'}
		self.__client.send_json(msg)
		self.__client.recv()
	def pause(self,host,ID):
		"""
		pause a docker container.
	  	@param host hostname of the VNF
	  	@param ID name or ID of the container
		"""
		msg = {'host' : host,'ID' : ID, 'action' : 'pause'}
		self.__client.send_json(msg)
		self.__client.recv()
	def unpause(self,host,ID):
		"""
		unpause a docker container.
	  	@param host hostname of the VNF
	  	@param ID name or ID of the container
		"""
		msg = {'host' : host,'ID' : ID, 'action' : 'unpause'}
		self.__client.send_json(msg)
		self.__client.recv()
	def destroy(self,host,ID):
		"""
		destroy a docker container.
	  	@param host hostname of the VNF
	  	@param ID name or ID of the container
		"""
		msg = {'host' : host,'ID' : ID, 'action' : 'destroy'}
		self.__client.send_json(msg)
		self.__client.recv()
	def deploy(self,host,user,image_name, vnf_name):
		"""
		deploy a docker container.
	  	@param host hostname of the VNF
	  	@param user name of the user who owns the VNF
	  	@param image_name docker image name for the VNF
	  	@param vnf_name name of the VNF instance
		"""
		msg = {'host' : host, 'user' : user, 'action' : 'deploy',
				'image_name' : image_name, 'vnf_name' : vnf_name, 'ID' : ''}
		self.__client.send_json(msg)
		self.__client.recv()
	def execute(self,host,ID,cmd):
		"""
		Executed commands inside a docker container.
		@param host hostname of the VNF
		@param ID name or ID of the container
		@param cmd the command to execute inside the container
		"""
		msg = {'host' : host,'ID' : ID, 'action' : 'execute', 'cmd' : cmd}
		self.__client.send_json(msg)
		self.__client.recv()
