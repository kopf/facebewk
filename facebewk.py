import json

import requests

BASE_URL = 'https://graph.facebook.com'

class Client(object):
    def __init__(self, access_token):
        """Accepts:
        access_token: an access token for an authenticated session
        """
        self.access_token = access_token

    def get(self, id=None, params=None, url=None):
        """Make a GET request to the Graph API, return a Node object"""
        if not id and not url:
            raise Exception('Either a Node ID or absolute URL must be specified.')
        params = self._sanitize_params(params)
        fetched = True

        if url:
            retval = self._get(None, params, full_url=url)
        else:
            if 'fields' in params:
                fetched = False
            retval = self._get(id, params)
        if 'id' in retval:
            return Node(retval, self, fetched=fetched)
        else:
            return Node._process_datapoint(retval, self)

    def _get(self, id, params, full_url=None):
        """Make a GET request to the Graph API, return a JSON object"""
        if full_url:
            retval = requests.get(full_url, params=params).json
        else:
            retval = requests.get('{0}/{1}'.format(BASE_URL, id),
                                  params=params).json
        self._check_error(retval)
        return retval

    def post(self, node, params):
        """Publish a post or comment to the Graph API"""
        params = self._sanitize_params(params)
        url = '{0}/{1}/'.format(BASE_URL, node.id)
        try:
            if node.type in ['post', 'status', 'link']:
                url += 'comments'
            else:
                url += 'feed'
        except AttributeError:
            url += 'feed'
        
        url += '?access_token={0}'.format(self.access_token)
        retval = requests.post(url, data=params).json
        self._check_error(retval)
        return Node(retval, self, fetched=False)

    def like(self, node, params=None):
        """'Like' a Node (post, link, comment, etc)"""
        params = self._sanitize_params(params)
        url = '{0}/{1}/likes/'.format(BASE_URL, node.id)
        retval = requests.post(url, data=params).json
        # successful 'like' operation should always return True:
        if retval is not True:
            self._check_error(retval)
        return retval

    def _sanitize_params(self, params):
        """Set default parameters, sanitize for a possible POST operation"""
        if not params:
            params = {}
        for key in params:
            if type(key) in [list, dict]:
                params[key] = json.dumps(params[key])
        params.setdefault('access_token', self.access_token)
        return params

    def _check_error(self, data):
        """Check for errors returned by the Graph API.
        data: should be a dictionary, or at least iterable.
        """
        if 'error' in data:
            raise ServerSideException(data['error'].get('message'))


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
            self.refresh() # this will automatically grab all node data
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

    def refresh(self):
        """Refresh a node's data"""
        self.__dict__ = self.__client__.get(self.id).__dict__

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
