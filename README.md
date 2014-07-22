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
>>> from facebewk import Client
>>> c = Client('FACEBOOK_USER_ACCESS_TOKEN')
>>> me = c.get('me')
>>> type(me)
<class 'facebewk.Node'>
>>> me['name']
u'Aengus Walton'
>>> type(me['hometown'])
<class 'facebewk.Node'>
>>> me['hometown']
{'__fetched__': False, u'id': u'110769XXXXXXXXX', u'name': u'Dublin, Ireland'}
>>> me['hometown']['checkins']
16734
>>> me['hometown']
{u'category': u'City', u'likes': 146053, '__fetched__': True, u'talking_about_count': 115999, u'name': u'Dublin, Ireland', u'link': u'http://www.facebook.com/pages/Dublin-Ireland/110769888951990', u'location': {u'latitude': 53.344037395687, u'longitude': -6.2632156999178}, u'is_community_page': True, u'checkins': 16734, u'id': u'110769888951990', u'is_published': True, u'description': u'<p><b>Dublin</b> is the capital and most populous city of ........'}
>>>
>>> newsfeed = c.get('/me/home')
>>> type(newsfeed)
<type 'dict'>
>>> type(newsfeed['data'])
<type 'list'>
>>>
>>> me['significant_other']
{'__fetched__': False, u'name': u'Patricia Korcz', u'id': u'100000XXXXXXXXX'}
>>> me['significant_other']['hometown']['checkins']
222
>>>
>>> status_update = c.post(me, {'message': 'writing my blog post innit', 
...     'privacy': {'value': 'CUSTOM', 'networks': 1, 'friends': 'NO_FRIENDS'}})
>>> status_update
{'__fetched__': False, u'id': u'37300126_632748066014'}
>>> status_update['message']
u'writing my blog post innit'
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
