class ResourceBroker(object):
    def __init__(self):
        self._resources = {}
        pass

    def register_resource(self, resource_key, resource_class, *args, **kwargs):
        if resource_key in self._resources.keys():
            raise Exception(resource_key + " already exists.")
        self._resources[resource_key] = resource_class(*args, **kwargs)

    def get_resource(self, resource_key):
        if resource_key not in self._resources:
            raise Exception(resource_key + " does not exist.")
        return self._resources[resource_key]
