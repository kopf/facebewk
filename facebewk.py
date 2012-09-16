import json


class Client(object):
    def __init__(self, access_token):
        self.access_token = access_token


class FacebookObject(object):
    def __init__(self, obj):
        if isinstance(obj, basestring):
            obj = json.loads(obj)
        for key in obj:
            setattr(self, key, self._process_datapoint(obj[key]))

    def _process_datapoint(self, data):
        if isinstance(data, list):
            data = [self._process_datapoint(entry) for entry in data]
        elif isinstance(data, dict):
            if 'id' in data:
                data = FacebookObject(data)
        return data