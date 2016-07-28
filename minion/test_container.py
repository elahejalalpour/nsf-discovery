from container_driver import ContainerDriver

mon = ContainerDriver()
mon.mock_mode()

def test_get_containers():
	assert(mon.containers()) != None

def test_start():
	assert(mon.start('whatever')) == 'container whatever started!'
	

print mon.get_id('nfuser-new-firewall')
