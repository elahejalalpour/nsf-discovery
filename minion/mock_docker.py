import errors
class Client:

    def __init__(self, base_url=""):
        self.base_url = base_url

    def containers(self, all=False):
        if(not all):
            data = [{
                'Status': 'Up 57 minutes',
                'Created': 1469639598, 'Image':
                'firewall', 'Labels': {},
                'NetworkSettings': {
                    'Networks': {
                        'bridge': {
                            'NetworkID':
                            '',
                            'MacAddress':
                            '02:42:ac:11:00:02',
                            'GlobalIPv6PrefixLen':
                            0,
                            'Links':
                            None,
                            'GlobalIPv6Address':
                            '',
                            'IPv6Gateway':
                            '',
                            'IPAMConfig':
                            None,
                            'EndpointID':
                            '1fbd43b6a9320e4e76e1b2d16e667ff3298ddef2c3312449869f7a50a61b30f1',
                            'IPPrefixLen':
                            16,
                            'IPAddress':
                            '172.17.0.2',
                            'Gateway':
                            '172.17.0.1',
                            'Aliases':
                            None
                        }
                    }
                }, 'HostConfig': {
                    'NetworkMode': 'default'
                }, 'ImageID': 'sha256:5fbc7e938c30d5919179a68718f19ab800f8e7dc7eddde995f11a83aebd396de',
                'State': 'running', 'Command':
                "/bin/bash -c 'ufw enable && ufw allow ssh && /usr/sbin/sshd -D'",
                'Names': ['/nfuser-new-firewall'],
                'Mounts': [], 'Id': 'd998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331',
                'Ports': [{
                    'Type': 'tcp',
                    'PrivatePort':
                    22
                }]
            }]
        else:
            data = [{
                'Status': 'Up 59 minutes',
                'Created': 1469639598, 'Image':
                'firewall', 'Labels': {},
                'NetworkSettings': {
                    'Networks': {
                        'bridge': {
                            'NetworkID':
                            '',
                            'MacAddress':
                            '02:42:ac:11:00:02',
                            'GlobalIPv6PrefixLen':
                            0,
                            'Links':
                            None,
                            'GlobalIPv6Address':
                            '',
                            'IPv6Gateway':
                            '',
                            'IPAMConfig':
                            None,
                            'EndpointID':
                            '1fbd43b6a9320e4e76e1b2d16e667ff3298ddef2c3312449869f7a50a61b30f1',
                            'IPPrefixLen':
                            16,
                            'IPAddress':
                            '172.17.0.2',
                            'Gateway':
                            '172.17.0.1',
                            'Aliases':
                            None
                        }
                    }
                }, 'HostConfig': {
                    'NetworkMode': 'default'
                }, 'ImageID': 'sha256:5fbc7e938c30d5919179a68718f19ab800f8e7dc7eddde995f11a83aebd396de',
                'State': 'running', 'Command':
                "/bin/bash -c 'ufw enable && ufw allow ssh && /usr/sbin/sshd -D'",
                'Names': ['/nfuser-new-firewall'],
                'Mounts': [], 'Id': 'd998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331',
                'Ports': [{
                    'Type': 'tcp',
                    'PrivatePort':
                    22
                }]
            }, {
                'Status': 'Exited (137) 25 hours ago',
                'Created': 1463075593, 'Image':
                    'firewall', 'Labels': {},
                    'NetworkSettings': {
                        'Networks': {
                            'bridge': {
                                'NetworkID':
                                    '',
                                    'MacAddress':
                                    '',
                                    'GlobalIPv6PrefixLen':
                                    0,
                                    'Links':
                                    None,
                                    'GlobalIPv6Address':
                                    '',
                                    'IPv6Gateway':
                                    '',
                                    'IPAMConfig':
                                    None,
                                    'EndpointID':
                                    '',
                                    'IPPrefixLen':
                                    0,
                                    'IPAddress':
                                    '',
                                    'Gateway':
                                    '',
                                    'Aliases':
                                    None
                            }
                        }
                    }, 'HostConfig': {
                        'NetworkMode': 'default'
                    }, 'ImageID': 'sha256:5fbc7e938c30d5919179a68718f19ab800f8e7dc7eddde995f11a83aebd396de',
                'State': 'exited', 'Command':
                    "/bin/bash -c 'ufw enable && ufw allow ssh && /usr/sbin/sshd -D'",
                    'Names': ['/nfuser-edge-ufw-1'],
                    'Mounts': [], 'Id': 'f5b716c6d757e97cdd2e2df2a7b37f357b946916787d681e8b29c62e0daa811e',
                    'Ports': []
            }]
        return data

    def inspect_container(self, container=None):
        if(container in 'd998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331' or
                container == 'nfuser-new-firewall'):
            data = {
                'ExecIDs': None,
                'State': {
                    'Status': 'running',
                    'Pid': 3790,
                    'OOMKilled': False,
                    'Dead': False,
                    'Paused': False,
                    'Running': True,
                    'FinishedAt': '0001-01-01T00:00:00Z',
                    'Restarting': False,
                    'Error': '',
                    'StartedAt': '2016-07-27T17:13:48.887176507Z',
                    'ExitCode': 0},
                'Config': {
                    'Tty': False,
                    'Cmd': [
                        '/bin/bash',
                        '-c',
                        'ufw enable && ufw allow ssh && /usr/sbin/sshd -D'],
                    'Volumes': None,
                    'Domainname': '',
                    'WorkingDir': '',
                    'Image': 'firewall',
                    'Hostname': 'd998116c3284',
                    'StdinOnce': False,
                    'Labels': {},
                    'AttachStdin': False,
                    'User': '',
                    'Env': [
                        'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                        'NOTVISIBLE=in users profile'],
                    'ExposedPorts': {
                        '22/tcp': {}},
                    'OnBuild': None,
                    'AttachStderr': True,
                    'Entrypoint': None,
                    'AttachStdout': True,
                    'OpenStdin': False},
                'ResolvConfPath': '/var/lib/docker/containers/d998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331/resolv.conf',
                'HostsPath': '/var/lib/docker/containers/d998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331/hosts',
                'Args': [
                    '-c',
                    'ufw enable && ufw allow ssh && /usr/sbin/sshd -D'],
                'Driver': 'aufs',
                'Path': '/bin/bash',
                'HostnamePath': '/var/lib/docker/containers/d998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331/hostname',
                'RestartCount': 0,
                'Name': '/nfuser-new-firewall',
                'Created': '2016-07-27T17:13:18.481285259Z',
                'GraphDriver': {
                                'Data': None,
                                'Name': 'aufs'},
                'Mounts': [],
                'ProcessLabel': '',
                                'NetworkSettings': {
                                    'Bridge': '',
                                    'Networks': {
                                        'bridge': {
                                            'NetworkID': 'b4a39361e286a51c5a4329cb9fb5b899b19512ffe1fb7c5a9f7421cb62cb5431',
                                            'MacAddress': '02:42:ac:11:00:02',
                                            'GlobalIPv6PrefixLen': 0,
                                            'Links': None,
                                            'GlobalIPv6Address': '',
                                            'IPv6Gateway': '',
                                            'IPAMConfig': None,
                                            'EndpointID': '1fbd43b6a9320e4e76e1b2d16e667ff3298ddef2c3312449869f7a50a61b30f1',
                                            'IPPrefixLen': 16,
                                            'IPAddress': '172.17.0.2',
                                            'Gateway': '172.17.0.1',
                                            'Aliases': None}},
                    'SecondaryIPv6Addresses': None,
                    'LinkLocalIPv6Address': '',
                                            'HairpinMode': False,
                                            'IPv6Gateway': '',
                                            'SecondaryIPAddresses': None,
                                            'SandboxID': '31ffa1d10bd725037ea4384d7be7f458e54ae82300e6384268754a72ee930dd0',
                                            'MacAddress': '02:42:ac:11:00:02',
                                            'GlobalIPv6Address': '',
                                            'Gateway': '172.17.0.1',
                                            'LinkLocalIPv6PrefixLen': 0,
                                            'EndpointID': '1fbd43b6a9320e4e76e1b2d16e667ff3298ddef2c3312449869f7a50a61b30f1',
                                            'SandboxKey': '/var/run/docker/netns/31ffa1d10bd7',
                                            'GlobalIPv6PrefixLen': 0,
                                            'IPPrefixLen': 16,
                                            'IPAddress': '172.17.0.2',
                                            'Ports': {
                                                '22/tcp': None}},
                'AppArmorProfile': '',
                'Image': 'sha256:5fbc7e938c30d5919179a68718f19ab800f8e7dc7eddde995f11a83aebd396de',
                'LogPath': '/var/lib/docker/containers/d998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331/d998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331-json.log',
                'HostConfig': {
                    'CpuPeriod': 0,
                    'MemorySwappiness': -1,
                    'ContainerIDFile': '',
                    'KernelMemory': 0,
                    'BlkioBps': 0,
                    'Memory': 0,
                    'CpuQuota': 0,
                    'UsernsMode': '',
                    'StorageOpt': None,
                    'AutoRemove': False,
                    'BlkioDeviceReadIOps': None,
                    'Dns': None,
                    'ExtraHosts': None,
                    'SandboxSize': 0,
                    'PidsLimit': 0,
                    'DnsSearch': None,
                    'Privileged': True,
                    'CpuPercent': 0,
                    'Ulimits': None,
                    'CpusetCpus': '',
                    'DiskQuota': 0,
                    'CgroupParent': '',
                    'BlkioWeight': 0,
                    'RestartPolicy': {
                        'MaximumRetryCount': 0,
                        'Name': ''},
                    'OomScoreAdj': 0,
                    'BlkioDeviceReadBps': None,
                    'VolumeDriver': '',
                    'ReadonlyRootfs': False,
                    'CpuShares': 0,
                    'PublishAllPorts': False,
                    'MemoryReservation': 0,
                    'BlkioWeightDevice': None,
                    'ConsoleSize': [
                        0,
                        0],
                    'NetworkMode': 'default',
                    'BlkioDeviceWriteBps': None,
                    'Isolation': '',
                    'GroupAdd': None,
                    'Devices': None,
                    'BlkioDeviceWriteIOps': None,
                    'Binds': None,
                    'CpusetMems': '',
                    'Cgroup': '',
                    'UTSMode': '',
                    'PidMode': '',
                    'VolumesFrom': None,
                    'CapDrop': None,
                    'DnsOptions': None,
                    'ShmSize': 67108864,
                    'Links': None,
                    'BlkioIOps': 0,
                    'IpcMode': '',
                    'PortBindings': None,
                    'SecurityOpt': None,
                    'CapAdd': None,
                    'CpuCount': 0,
                    'MemorySwap': 0,
                    'OomKillDisable': False,
                    'LogConfig': {
                        'Config': {},
                        'Type': 'json-file'}},
                'Id': 'd998116c32849114eae8152c060fcd4cc12989e9b3a1c71e6172d42fa43a9331',
                'MountLabel': ''}
        elif(container in 'f5b716c6d757e97cdd2e2df2a7b37f357b946916787d681e8b29c62e0daa811e' or
                container == 'nfuser-edge-ufw-1'):
            data = {
                'ExecIDs': None,
                'State': {
                    'Status': 'exited',
                    'Pid': 0,
                    'OOMKilled': False,
                    'Dead': False,
                    'Paused': False,
                    'Running': False,
                    'FinishedAt': '2016-07-26T16:45:34.225962598Z',
                    'Restarting': False,
                    'Error': '',
                    'StartedAt': '2016-07-26T16:45:01.117915909Z',
                    'ExitCode': 137},
                'Config': {
                    'Tty': False,
                    'Cmd': [
                        '/bin/bash',
                        '-c',
                        'ufw enable && ufw allow ssh && /usr/sbin/sshd -D'],
                    'Volumes': None,
                    'Domainname': '',
                    'WorkingDir': '',
                    'Image': 'firewall',
                    'Hostname': '127.0.0.1',
                    'StdinOnce': False,
                    'Labels': {},
                    'AttachStdin': False,
                    'User': '',
                    'Env': [
                        'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                        'NOTVISIBLE=in users profile'],
                    'ExposedPorts': {
                        '22/tcp': {}},
                    'OnBuild': None,
                    'AttachStderr': True,
                    'Entrypoint': None,
                    'AttachStdout': True,
                    'OpenStdin': False},
                'ResolvConfPath': '/var/lib/docker/containers/f5b716c6d757e97cdd2e2df2a7b37f357b946916787d681e8b29c62e0daa811e/resolv.conf',
                'HostsPath': '/var/lib/docker/containers/f5b716c6d757e97cdd2e2df2a7b37f357b946916787d681e8b29c62e0daa811e/hosts',
                'Args': [
                    '-c',
                    'ufw enable && ufw allow ssh && /usr/sbin/sshd -D'],
                'Driver': 'aufs',
                'Path': '/bin/bash',
                'HostnamePath': '/var/lib/docker/containers/f5b716c6d757e97cdd2e2df2a7b37f357b946916787d681e8b29c62e0daa811e/hostname',
                'RestartCount': 0,
                'Name': '/nfuser-edge-ufw-1',
                'Created': '2016-05-12T17:53:13.846817415Z',
                'GraphDriver': {
                                'Data': None,
                                'Name': 'aufs'},
                'Mounts': [],
                'ProcessLabel': '',
                                'NetworkSettings': {
                                    'Bridge': '',
                                    'Networks': {
                                        'bridge': {
                                            'NetworkID': '327bcdea10c03bdd18fe4df73fc13b79992f12750ff0954d3aa13468b851b653',
                                            'MacAddress': '',
                                            'GlobalIPv6PrefixLen': 0,
                                            'Links': None,
                                            'GlobalIPv6Address': '',
                                            'IPv6Gateway': '',
                                            'IPAMConfig': None,
                                            'EndpointID': '',
                                            'IPPrefixLen': 0,
                                            'IPAddress': '',
                                            'Gateway': '',
                                            'Aliases': None}},
                    'SecondaryIPv6Addresses': None,
                    'LinkLocalIPv6Address': '',
                                            'HairpinMode': False,
                                            'IPv6Gateway': '',
                                            'SecondaryIPAddresses': None,
                                            'SandboxID': 'ba9ae97d4cea1bb32595e7163b518572a24677331688cb9656af2d26ff9b0829',
                                            'MacAddress': '',
                                            'GlobalIPv6Address': '',
                                            'Gateway': '',
                                            'LinkLocalIPv6PrefixLen': 0,
                                            'EndpointID': '',
                                            'SandboxKey': '/var/run/docker/netns/ba9ae97d4cea',
                                            'GlobalIPv6PrefixLen': 0,
                                            'IPPrefixLen': 0,
                                            'IPAddress': '',
                                            'Ports': None},
                'AppArmorProfile': '',
                'Image': 'sha256:5fbc7e938c30d5919179a68718f19ab800f8e7dc7eddde995f11a83aebd396de',
                'LogPath': '/var/lib/docker/containers/f5b716c6d757e97cdd2e2df2a7b37f357b946916787d681e8b29c62e0daa811e/f5b716c6d757e97cdd2e2df2a7b37f357b946916787d681e8b29c62e0daa811e-json.log',
                'HostConfig': {
                    'CpuPeriod': 0,
                    'MemorySwappiness': -1,
                    'ContainerIDFile': '',
                    'KernelMemory': 0,
                    'BlkioBps': 0,
                    'Memory': 0,
                    'CpuQuota': 0,
                    'UsernsMode': '',
                    'StorageOpt': None,
                    'AutoRemove': False,
                    'BlkioDeviceReadIOps': None,
                    'Dns': ['8.8.8.8'],
                    'ExtraHosts': None,
                    'SandboxSize': 0,
                    'PidsLimit': 0,
                    'DnsSearch': [],
                    'Privileged': True,
                    'CpuPercent': 0,
                    'Ulimits': None,
                    'CpusetCpus': '',
                    'DiskQuota': 0,
                    'CgroupParent': '',
                    'BlkioWeight': 0,
                    'RestartPolicy': {
                        'MaximumRetryCount': 0,
                        'Name': ''},
                    'OomScoreAdj': 0,
                    'BlkioDeviceReadBps': None,
                    'VolumeDriver': '',
                    'ReadonlyRootfs': False,
                    'CpuShares': 0,
                    'PublishAllPorts': False,
                    'MemoryReservation': 0,
                    'BlkioWeightDevice': None,
                    'ConsoleSize': [
                        0,
                        0],
                    'NetworkMode': 'default',
                    'BlkioDeviceWriteBps': None,
                    'Isolation': '',
                    'GroupAdd': None,
                    'Devices': None,
                    'BlkioDeviceWriteIOps': None,
                    'Binds': None,
                    'CpusetMems': '',
                    'Cgroup': '',
                    'UTSMode': '',
                    'PidMode': '',
                    'VolumesFrom': None,
                    'CapDrop': None,
                    'DnsOptions': [],
                    'ShmSize': 67108864,
                    'Links': None,
                    'BlkioIOps': 0,
                    'IpcMode': '',
                    'PortBindings': None,
                    'SecurityOpt': None,
                    'CapAdd': None,
                    'CpuCount': 0,
                    'MemorySwap': 0,
                    'OomKillDisable': False,
                    'LogConfig': {
                        'Config': {},
                        'Type': 'json-file'}},
                'Id': 'f5b716c6d757e97cdd2e2df2a7b37f357b946916787d681e8b29c62e0daa811e',
                'MountLabel': ''}
        else:
            raise errors.VNFNotFoundError
        return data

    def execute(self, vnf_name, args, stdout=True, stderr=False):
        return None

    def start(self, container='', dns='8.8.8.8', privileged=False):
        #data = inspect_container(container)
        print('container ' + container + ' started!')

    def restart(self, container=''):
        print('container ' + container + ' restarted!')

    def stop(self, container=''):
        print('container ' + container + ' stopped!')

    def pause(self, container=''):
        print('container ' + container + ' paused!')

    def unpause(self, container=''):
        print('container ' + container + ' unpaused!')

    def create_container(self, image='', name='', host_config='', **kwargs):
        print('container ' + name + ' created!')
        return {'Id': '0000000000'}

    def remove_container(self, container='', force=False):
        print('container ' + container + ' removed!')

    def images(self):
        data = [{'Created': 1462317064,
                 'Labels': {},
                 'VirtualSize': 187939781,
                 'ParentId': 'sha256:3d707bd2df834a2a16dda05d850e7f77e538fb2cb112c7167d579752456a3741',
                 'RepoTags': ['ubuntu:14.04'],
                 'RepoDigests': None,
                 'Id': 'sha256:90d5884b1ee07f7f791f51bab92933943c87357bcd2fa6be0e82c48411bbb653',
                 'Size': 187939781},
                {'Created': 1455631935,
                 'Labels': {},
                 'VirtualSize': 216001137,
                 'ParentId': 'sha256:c75b33c0d81fe19b1eb05e2268bbf082ee4ca3dba7290646fcf3f9821fafe367',
                 'RepoTags': ['firewall:latest'],
                 'RepoDigests': None,
                 'Id': 'sha256:5fbc7e938c30d5919179a68718f19ab800f8e7dc7eddde995f11a83aebd396de',
                 'Size': 216001137},
                {'Created': 1453830514,
                 'Labels': None,
                 'VirtualSize': 131274281,
                 'ParentId': 'sha256:3e340441a556b66e2b0b93b84564ee06026574c5ce6c04eade306ee06e64919c',
                 'RepoTags': ['ubuntu:15.04'],
                 'RepoDigests': None,
                 'Id': 'sha256:d1b55fd07600b2e26d667434f414beee12b0771dfd4a2c7b5ed6f2fc9e683b43',
                 'Size': 131274281},
                {'Created': 1453246284,
                 'Labels': None,
                 'VirtualSize': 187899635,
                 'ParentId': 'sha256:039f1bb3922f20162d1f2e43dc308a21fb975eed0990f31fedd0cc19b4e335ab',
                 'RepoTags': ['ubuntu:latest'],
                 'RepoDigests': None,
                 'Id': 'sha256:3876b81b5a81678926c601cd842040a69eb0456d295cd395e7a895a416cf7d91',
                 'Size': 187899635}]
        return data
