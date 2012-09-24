import json
from urllib import urlencode
import urlparse

import requests

BASE_URL = 'https://graph.facebook.com'

class Client(object):
    def __init__(self, access_token):
        self.access_token = access_token

    def get(self, id=None, params=None, path=None):
        """Make a GET request to the Graph API, return a Node object"""
        if not id and not path:
            raise Exception('Either a Node ID or URL path must be specified.')
        fetched = True
        if params is None:
            params = {}
        params.setdefault('access_token', self.access_token)

        if path:
            retval = self._get(None, params, path=path)
        else:
            if 'fields' in params:
                fetched = False
            retval = self._get(id, params)
        return Node(retval, self, fetched=fetched)

    def _get(self, id, params, path=None):
        """Make a GET request to the Graph API, return a JSON object"""
        if path:
            url_parts = list(urlparse.urlparse(path))
            base_url = list(urlparse.urlparse(BASE_URL))
            for i in range(0, 2):
                url_parts[i] = base_url[i]
            qsl = urlparse.parse_qs(url_parts[4])
            qsl.update(params)
            url_parts[4] = urlencode([(key, qsl[key]) for key in qsl])
            url = urlparse.urlunparse(url_parts)
        else:
            url = '{0}/{1}?{2}'.format(BASE_URL, id, urlencode(params))
        raw_data = requests.get(url).content
        retval = json.loads(raw_data)
        if 'error' in retval:
            raise ServerSideException(retval['error'].get('message'))
        return json.loads(raw_data)

    def post(self, node, params):
        """Publish a post or comment to the Graph API"""
        params.setdefault('access_token', self.access_token)
        url = '{0}/{1}/'.format(BASE_URL, node.id)
        try:
            if node.type in ['post', 'status', 'link']:
                url += 'comments'
            else:
                url += 'feed'
        except AttributeError:
            url += 'feed'
        retval = json.loads(requests.post(url, params).content)
        if 'error' in retval:
            raise ServerSideException(retval['error'].get('message'))
        return Node(retval, self, fetched=False)

    def like(self, node, params=None):
        if not params:
            params = {}
        params.setdefault('access_token', self.access_token)
        url = '{0}/{1}/likes/'.format(BASE_URL, node.id)
        raw_data = requests.post(url, params)
        return json.loads(raw_data.content)

    def get_newsfeed(self, params=None):
        if not params:
            params = {}
        params.setdefault('access_token', self.access_token)
        data = self._get(None, params, path='/me/home')
        return Node._process_datapoint(data, self)


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
            setattr(self, key, self._process_datapoint(obj[key], self.__client__))

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
                msg = "Node {0} of type '{1}' has no attribute '{2}'".format(self.id,
                    self.type, name)
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
            return "<Facebook Node {0} of type '{1}'>".format(self.id, self.type)
        elif 'id' in self.__dict__:
            return "<Facebook Node {0}>".format(self.id)
        else:
            return "<Facebook Node>"

    @classmethod
    def _process_datapoint(node, data, client):
        """Process json data from facebook, recursively if necessary, 
        producing Node objects where possible.
        """
        if isinstance(data, list):
            data = [node._process_datapoint(entry, client) for entry in data]
        elif isinstance(data, dict):
            if 'id' in data:
                data = Node(data, client)
            else:
                for key in data:
                    data[key] = node._process_datapoint(data[key], client)
        return data


class ServerSideException(Exception):
    pass
