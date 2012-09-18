import json

import requests


class Client(object):
    def __init__(self, access_token):
        self.access_token = access_token

    def get(self, id):
        raw_data = requests.get('https://graph.facebook.com/{0}?access_token={1}'.format(id, self.access_token)).content
        return json.loads(raw_data)


class Node(object):
    def __init__(self, obj, client, fetched=False):
        self.__client__ = client
        self.__fetched__ = fetched
        if isinstance(obj, basestring):
            obj = json.loads(obj)
        for key in obj:
            setattr(self, key, self._process_datapoint(obj[key]))

    def __getattr__(self, name):
        if hasattr(self, 'id') and not self.__fetched__:
            self.__dict__ = Node(self.__client__.get(self.id), self.__client__, fetched=True).__dict__
            if name in self.__dict__:
                return self.__getattribute__(name)
        if 'type' in self.__dict__:
            raise AttributeError("Node of type '{0}' has no attribute '{1}'".format(self.type, name))
        raise AttributeError("Node has no attribute '{0}'".format(name))

    def __repr__(self):
        if 'type' in self.__dict__:
            return "<Facebook Node {0} of type {1}>".format(self.id, self.type)
        return "<Facebook Node {0}>".format(self.id)

    def _process_datapoint(self, data):
        if isinstance(data, list):
            data = [self._process_datapoint(entry) for entry in data]
        elif isinstance(data, dict):
            if 'id' in data:
                data = Node(data, self.__client__)
            else:
                for key in data:
                    data[key] = self._process_datapoint(data[key])
        return data
