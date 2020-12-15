import urllib.request, urllib.error, urllib.parse, json, webbrowser, jinja2, logging
from flask import Flask, render_template, request


### Utility functions you may want to use
def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


def safe_get(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print("The server couldn't fulfill the request.")
        print("Error code: ", e.code)
    except urllib.error.URLError as e:
        print("We failed to reach a server")
        print("Reason: ", e.reason)
    return None


#### Main Assignment ##############

# You need to get your own api_key from Flickr,
# from here https://www.flickr.com/services/api/misc.api_keys.html
# (You will need to create an account).
#
# Put it in the file flickr_key.py
#
# Then, UNCOMMENT the api_key line AND the params['api_key'] line in
# the function below.
#

import flickr_key as flickr_key


def flickrREST(baseurl='https://api.flickr.com/services/rest/',
               method='flickr.photos.search',
               api_key=flickr_key.key,
               format='json',
               params={},
               printurl=False
               ):
    params['method'] = method
    params['api_key'] = api_key
    params['format'] = format
    if format == "json": params["nojsoncallback"] = True
    url = baseurl + "?" + urllib.parse.urlencode(params)
    if printurl:
        print(url)
    return safe_get(url)


#######################
## Building block 1 ###
# Define a function called get_photo_ids() which uses the Flickr API
# to search for photos with a given tag, and return a list of photo
# IDs for the corresponding photos.
#
# * Use a list comprehension to generate the list. *


def get_photo_ids(tag, n=100):
    params = {'tags': tag, 'per_page': n}
    flickr_url = flickrREST(params=params)
    flickr_str = flickr_url.read()
    flickr_data = json.loads(flickr_str)
    return [photo['id'] for photo in flickr_data['photos']['photo']]


######################
## Building block 2 ##
#
# Define a function called get_photo_info() which uses the Flickr API
# to get information about a particular photo id. The information
# should be returned as a dictionary Hint: use flickrREST and the
# Flickr API method flickr.photos.getInfo, documented at
# http://www.flickr.com/services/api/flickr.photos.getInfo.html


def get_photo_info(photoid):
    params = {'photo_id': photoid}
    flickr_info_url = flickrREST(method="flickr.photos.getInfo", params=params)
    flickr_info_str = flickr_info_url.read()
    flickr_data = json.loads(flickr_info_str)
    return flickr_data['photo']

