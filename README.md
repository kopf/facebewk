# facebewk

[![Build Status](https://travis-ci.org/kopf/facebewk.svg?branch=master)](https://travis-ci.org/kopf/facebewk)

facebewk is a clever little Python wrapper for the facebook Graph API. 

It is designed to minimise the number of HTTP requests, while providing a developer-friendly, dynamic representation of
data pulled from the API. 

## Getting Started

### Requirements

`pip install -r requirements.txt`

Then, get an API access token, create your Client object, and start querying!

## Using facebewk

[Click here](http://ventolin.org/2012/09/facebewk) to read a blog-post I wrote when I released facebewk. 

It can be fairly well summarised in the following interactive python session:

````python
>>> # Start by creating a client with your user access token:
>>> from facebewk import Client
>>> c = Client('FACEBOOK_USER_ACCESS_TOKEN')
>>> 
>>> # This will create a Node object representing your profile:
>>> me = c.get('me')
>>> type(me)
<class 'facebewk.Node'>
>>> me['name']
u'Aengus Walton'
>>> # facebewk has noticed that my 'hometown' is a link to another node on
>>> # the facebook graph and treated it as such:
>>> type(me['hometown'])
<class 'facebewk.Node'>
>>> # We still have relatively little information on it, though:
>>> me['hometown']
{'__fetched__': False, u'id': u'110769XXXXXXXXX', u'name': u'Dublin, Ireland'}
>>> 
>>> # Referring to the facebook graph API documentation, we see we should be
>>> # able to find the number of checkins in a town.
>>> # If we try to simply access it, a HTTP request will be automatically
>>> # performed and we'll have the data:
>>> me['hometown']['checkins']
16734
>>> # We can see what effect this has had by inspecting the object again:
>>> me['hometown']
{u'category': u'City', u'likes': 146053, '__fetched__': True, u'talking_about_count': 115999, u'name': u'Dublin, Ireland', u'link': u'http://www.facebook.com/pages/Dublin-Ireland/110769888951990', u'location': {u'latitude': 53.344037395687, u'longitude': -6.2632156999178}, u'is_community_page': True, u'checkins': 16734, u'id': u'110769888951990', u'is_published': True, u'description': u'<p><b>Dublin</b> is the capital and most populous city of ........'}
>>>
>>> # Another example - 'significant_other' also points to, of course, another facebook node:
>>> me['significant_other']['hometown']['checkins']
222
>>>
>>> # Your newsfeed can be parsed and inspected:
>>> newsfeed = c.get('/me/home')
>>> type(newsfeed)
<type 'dict'>
>>> type(newsfeed['data'])
<type 'list'>
>>>
>>> # Using facebewk, you can also create and alter data on the graph.
>>> # Here, we'll make a post to the 'me' object (a facebook profile):
>>> status_update = c.post(me, {'message': 'writing my blog post innit', 
...     'privacy': {'value': 'CUSTOM', 'networks': 1, 'friends': 'NO_FRIENDS'}})
>>> status_update
{'__fetched__': False, u'id': u'37300126_632748066014'}
>>> status_update['message']
u'writing my blog post innit'
>>>
>>> # Whereas making a post to a status update will result in
>>> # a comment being posted to it:
>>> my_comment = c.post(status_update, {'message': 'blablabla'})
>>> c.like(my_comment)
True
````

The last few lines result in the following appearing on my profile:

![facebook post screenshot](http://ventolin.org/wp-content/uploads/2012/09/example_status_update.png)

## Tests

````
pip install -r test_requirements.txt
nosetests
````
