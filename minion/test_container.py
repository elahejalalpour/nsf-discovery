from container_driver import ContainerDriver

mon = ContainerDriver(True)

def test_get_containers():
	assert(mon.get_containers() != None)

def test_start():
	assert(mon.start('whatever') == 'container whatever started!')
	
test_get_containers()
