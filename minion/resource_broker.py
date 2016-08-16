class ResourceBroker(object):

    def __init__(self):
        self._resources = {}
        pass

    def register_resource(self, resource_key, resource, *args, **kwargs):
        if resource_key in self._resources.keys():
            raise Exception(resource_key + " already exists.")
        if callable(resource):
            self._resources[resource_key] = resource(*args, **kwargs)
        else:
            self._resources[resource_key] = resource

    def get_resource(self, resource_key):
        if not self._resources.has_key(resource_key):
            raise Exception(resource_key + " does not exist.")
        return self._resources[resource_key]
