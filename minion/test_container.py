from container_driver import ContainerDriver

mon = ContainerDriver(True)

def test_get_containers():
	assert(mon.get_containers() != None)

def test_get_id():
	assert(mon.get_id('nfuser-new-firewall') == 'd998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331')
	
test_get_containers()
