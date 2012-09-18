import json

import requests


class Client(object):
    def __init__(self, access_token):
        self.access_token = access_token

    def get(self, id):
        raw_data = requests.get('https://graph.facebook.com/{0}?access_token={1}'.format(id, self.access_token)).content
        return json.loads(raw_data)


class FacebookObject(object):
    def __init__(self, obj, fetched=False):
        self.__fetched__ = fetched
        if isinstance(obj, basestring):
            obj = json.loads(obj)
        for key in obj:
            setattr(self, key, self._process_datapoint(obj[key]))

    def __getattr__(self, name):
        if hasattr(self, 'id') and not self.__fetched__:
            client = Client('AAAFEAjFZCzHUBALPONCwLZA2GBXIkm1joYkB0rZANqbcU83iILOzwexL5DreZAJcCBxRiorhZC6JlUY6fDZANyGxKcIzKzVEtk9G1psiHZB1gZDZD')
            self.__dict__ = FacebookObject(client.get(self.id), fetched=True).__dict__
            return self.__getattribute__(name)
        raise AttributeError("'FacebookObject' object has no attribute '{0}'".format(name))

    def _process_datapoint(self, data):
        if isinstance(data, list):
            data = [self._process_datapoint(entry) for entry in data]
        elif isinstance(data, dict):
            if 'id' in data:
                data = FacebookObject(data)
            else:
                for key in data:
                    #if key in ['likes', 'comments']:
                    #    data[key] = self._process_datapoint(data[key].get('data', []))
                    #else:
                    data[key] = self._process_datapoint(data[key])
        return data
