import json
from urllib import urlencode

import requests


class Client(object):
    def __init__(self, access_token):
        self.access_token = access_token

    def get(self, id, params=None, path=None):
        """Make a GET request to the Graph API, return a Node object"""
        if path:
            retval = self._get(None, {}, path=path)
        else:
            if params is None:
                params = {}
            fetched = True
            if 'fields' in params:
                fetched = False

            params.setdefault('access_token', self.access_token)
            retval = self._get(id, params)
        if 'error' in retval:
            raise ServerSideException(retval['error'].get('message'))
        return Node(retval, self, fetched=fetched)

    def _get(self, id, params, path=None):
        """Make a GET request to the Graph API, return a JSON object"""
        url = 'https://graph.facebook.com'
        if path:
            url += path
        else:
            url += '/{0}?{1}'.format(id, urlencode(params))
        raw_data = requests.get(url).content
        return json.loads(raw_data)


class Node(object):
    def __init__(self, obj, client, fetched=False):
        """Accepts:
        obj: JSON-parsed response from Graph API
        client: facebewk.Client object
        fetched: Whether the entire object has been fetched
        """
        self.__client__ = client
        self.__fetched__ = fetched
        if isinstance(obj, basestring):
            obj = json.loads(obj)
        for key in obj:
            setattr(self, key, self._process_datapoint(obj[key]))

    def __getattr__(self, name):
        """Executed when a non-existant Node attribute is accessed.
        If we haven't already fetched the full Node, then fetch it
        and try again to return the attribute.
        Otherwise raise an AttributeError.
        """
        if hasattr(self, 'id') and not self.__fetched__:
            self.__dict__ = self.__client__.get(self.id).__dict__
            if name in self.__dict__:
                return self.__getattribute__(name)

            if 'type' in self.__dict__:
                msg = "Node {0} of type '{1}' has no attribute '{2}'".format(self.id, self.type, name)
            else:
                msg = "Node {0} has no attribute '{1}'".format(self.id, name)
        else:
            if 'type' in self.__dict__:
                msg = "Node of type '{0}' has no attribute '{1}'".format(self.type, name)
            else:
                msg = "Node has no attribute '{0}'".format(name)
        raise AttributeError(msg)

    def __repr__(self):
        if 'type' in self.__dict__:
            return "<Facebook Node {0} of type {1}>".format(self.id, self.type)
        return "<Facebook Node {0}>".format(self.id)

    def _process_datapoint(self, data):
        """Process raw data from facebook, recursively if necessary, 
        producing Node objects where possible.
        """
        if isinstance(data, list):
            data = [self._process_datapoint(entry) for entry in data]
        elif isinstance(data, dict):
            if 'id' in data:
                data = Node(data, self.__client__)
            else:
                for key in data:
                    data[key] = self._process_datapoint(data[key])
        return data


class ServerSideException(Exception):
    pass