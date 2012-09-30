import copy
import json
import unittest

from mock import patch
import requests

from facebewk import Client, Node, ServerSideException, BASE_URL

def _build_response_obj(node_id, status_code=200):
    r = requests.Response()
    r.status_code = status_code
    r._content = _get_fixture(node_id)
    r._json = json.loads(r._content)
    return r


def _get_fixture(id):
    retval = None
    with open('fixtures/{0}.json'.format(id), 'r') as f:
        retval = f.read()
    return retval


class BaseTestCase(unittest.TestCase):
    """Basic setup common to all tests"""
    access_token = 'access_token_blah'
    c = Client(access_token)
    default_params = {'access_token': access_token}
    user_node = Node(_get_fixture(1000), None, fetched=True)
    status_node = Node(_get_fixture('status_fetched'), None)
    post_node = Node(_get_fixture('post_fetched'), None)
    link_node = Node(_get_fixture('link_fetched'), None)
    message = {'message': 'an example post payload'}
    default_post_params = copy.copy(default_params)
    default_post_params['message'] = message['message']
    privacy_dict = {'value': 'CUSTOM', 'networks': 1, 'friends': 'NO_FRIENDS'}


class TestClient(BaseTestCase):
    def test_client_fails_without_id_or_url(self):
        """Should raise an exception when neither id nor url are provided"""
        self.assertRaises(Exception, self.c.get, params={'bla': 'bla'})
        self.assertRaises(Exception, self.c.get)

    def test_use_full_url_when_provided(self):
        """Should give preference to url if provided"""
        user_defined_url = 'http://bleepbloop.com/xyz'
        with patch.object(requests, 'get') as mocked_get:
            self.c.get(url=user_defined_url)
            mocked_get.assert_called_with(user_defined_url, params=self.default_params)

            self.c.get(id='12345', url=user_defined_url)
            mocked_get.assert_called_with(user_defined_url, params=self.default_params)

    def test_use_params_when_provided(self):
        """Should use parameters when provided"""
        passed_params = {'abc': 'def'}
        expected_params = self.default_params
        expected_params['abc'] = 'def'
        with patch.object(requests, 'get') as mocked_get:
            self.c.get(id='xyz', params=passed_params)
            mocked_get.assert_called_with(BASE_URL+'/xyz', params=expected_params)

    def test_should_automatically_create_node(self):
        """Should create a node when the graph api returns JSON with 'id' in it"""
        node_id = 1000
        with patch.object(requests, 'get') as mocked_get:
            mocked_get.return_value = _build_response_obj(node_id)
            retval = self.c.get(node_id)
        self.assertTrue(isinstance(retval, Node))

    def test_should_not_create_node_from_non_node_value(self):
        """Should not create a node from JSON that doesn't resemble a node"""
        with patch.object(requests, 'get') as mocked_get:
            mocked_get.return_value = _build_response_obj('newsfeed')
            retval = self.c.get('newsfeed')
        self.assertFalse(isinstance(retval, Node))

    def test_should_recursively_create_nodes_in_non_node_object(self):
        """Should recurse through returned JSON and create Nodes as appropriate"""
        with patch.object(requests, 'get') as mocked_get:
            mocked_get.return_value = _build_response_obj('newsfeed')
            retval = self.c.get('newsfeed')
        self.assertFalse(isinstance(retval, Node))
        self.assertTrue(isinstance(retval['data'][0], Node))
        self.assertTrue(isinstance(retval['data'][1], Node))

    def test_post_to_feed_when_user_node_provided(self):
        """Should make a post to a user's feed when it's passed to post()"""
        with patch.object(requests, 'post') as mocked_post:
            mocked_post.return_value = _build_response_obj('post_unfetched')
            retval = self.c.post(self.user_node, self.message)
            mocked_post.assert_called_with(
                '{0}/{1}/feed?access_token={2}'.format(BASE_URL,
                                                       self.user_node['id'],
                                                       self.access_token),
                data=self.default_post_params
            )
    
    def test_post_as_comment_when_status_provided(self):
        """Should make a comment on a status when it's passed to post()"""
        with patch.object(requests, 'post') as mocked_post:
            mocked_post.return_value = _build_response_obj('comment_unfetched')
            retval = self.c.post(self.status_node, self.message)
            mocked_post.assert_called_with(
                '{0}/{1}/comments?access_token={2}'.format(BASE_URL,
                                                       self.status_node['id'],
                                                       self.access_token),
                data=self.default_post_params
            )

    def test_post_as_comment_when_link_provided(self):
        """Should make a comment on a link when it's passed to post()"""
        with patch.object(requests, 'post') as mocked_post:
            mocked_post.return_value = _build_response_obj('comment_unfetched')
            retval = self.c.post(self.link_node, self.message)
            mocked_post.assert_called_with(
                '{0}/{1}/comments?access_token={2}'.format(BASE_URL,
                                                       self.link_node['id'],
                                                       self.access_token),
                data=self.default_post_params
            )

    def test_post_as_comment_when_post_provided(self):
        """Should make a comment on a post when it's passed to post()"""
        with patch.object(requests, 'post') as mocked_post:
            mocked_post.return_value = _build_response_obj('comment_unfetched')
            retval = self.c.post(self.post_node, self.message)
            mocked_post.assert_called_with(
                '{0}/{1}/comments?access_token={2}'.format(BASE_URL,
                                                       self.post_node['id'],
                                                       self.access_token),
                data=self.default_post_params
            )

    def test_sanitize_params_inserts_access_token_by_default(self):
        """Should insert access token of Client object by default"""
        retval = self.c._sanitize_params({})
        self.assertTrue('access_token' in retval)
        self.assertEquals(retval['access_token'], self.c.access_token)

    def test_sanitize_params_only_jsonifies_dicts_lists(self):
        """Should only jsonify dicts and lists to be posted"""
        payload = {'message': 'abc', 'privacy': self.privacy_dict, 'xyz': ['a','b']}
        retval = self.c._sanitize_params(payload)
        self.assertEquals(retval, 
            {'access_token': self.access_token,
             'message': 'abc', 
             'privacy': json.dumps(self.privacy_dict),
             'xyz': json.dumps(['a','b'])})

    def test_check_errors_raises_error(self):
        """Should raise error when 'error' in graph api return value"""
        self.assertRaises(Exception, self.c._check_error,
                          json.loads(_get_fixture('error')))

    def test_check_errors_called_in_get(self):
        """Should always check for errors when getting content from graph"""
        with patch.object(requests, 'get') as mocked_get:
            mocked_get.return_value = _build_response_obj('error')
            self.assertRaises(ServerSideException, self.c.get, 'xyz')

    def test_check_errors_called_in_post(self):
        """Should always check for errors when posting content to the graph"""
        with patch.object(requests, 'post') as mocked_post:
            mocked_post.return_value = _build_response_obj('error')
            self.assertRaises(ServerSideException, self.c.post, self.post_node, {})

    def test_check_errors_called_in_like(self):
        """Should check for errors when liking content on the graph if retval != True"""
        with patch.object(requests, 'post') as mocked_post:
            mocked_post.return_value = _build_response_obj('error')
            self.assertRaises(ServerSideException, self.c.like, self.post_node, {})

    def test_check_errors_not_called_in_like(self):
        """Should not check for errors when liking content on the graph if retval == True"""
        with patch.object(requests, 'post') as mocked_post:
            mocked_post.return_value = _build_response_obj('like_success')
            with patch.object(Client, '_check_error') as check_error:
                self.c.like(self.post_node)
                self.assertFalse(check_error.called)

class TestNode(BaseTestCase):
    def setUp(self):
        self.user_node = Node(_get_fixture(1000), Client('xyz'), fetched=True)

    def test_check_if_id_in_raw_data(self):
        """Should raise an exception when no 'id' key is found in data"""
        self.assertRaises(Exception, Node.__init__, {}, None)

    def test_check_if_node_is_processed_recursively(self):
        """Should recursively make subnodes when creating a node"""
        self.assertTrue(isinstance(self.user_node['significant_other'], Node))
        self.assertTrue(isinstance(self.user_node['hometown'], Node))
        self.assertTrue(isinstance(self.user_node['education'][0]['school'], Node))

    def test_take_fetched_into_account(self):
        """Should not try to fetch more information when the entire node is fetched"""
        with patch.object(requests, 'get') as mocked_get:
            try:
                _ = self.user_node['non_existant_key']
            except Exception:
                pass
            self.assertFalse(mocked_get.called)

    def test_get_if_not_fully_fetched(self):
        """Should try to fetch more information when the entire node isn't fetched"""
        with patch.object(requests, 'get') as mocked_get:
            try:
                _ = self.user_node['significant_other']['non_existant_key']
            except Exception:
                pass
            self.assertTrue(mocked_get.called)

    def test_raise_exception_if_node_fetched_and_non_existant_key_accessed(self):
        """Should raise a KeyError when a non-existant key is accessed for a fully-fetched node"""
        with patch.object(requests, 'get') as mocked_get:
            try:
                _ = self.user_node['significant_other']['non_existant_key']
            except KeyError:
                pass
            else:
                self.assertEquals(1, 2)

    