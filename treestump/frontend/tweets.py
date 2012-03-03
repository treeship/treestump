#!/usr/bin/python

# NOTE: You need a settings.py file with certain oauth tokens for
# twitter and foursquare.  I can give you mine but I don't want to
# check them in publicly (neha).
#
# To find interesting hash tags near Cambridge:
#   python tweets.py   
#
# To find interesting hash tags somewhere else:
#   python tweets.py lat long

import twitter
import sys
from venues import Foursquare
import os
sys.path.append( os.path.join(os.path.dirname(__file__), '..') )
from settings import *



cambridge_lat = 42.363
cambridge_long = -71.084
radius = '10mi'

def get_api():
    api = twitter.Api(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, 
                      TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    return api

def twitter_call(term, geo):
    api = get_api()
    results = api.GetSearch(term=term, geocode=geo)
    return results

def popular_hashtags(lat, long):
    hashtags = {}
    fs = Foursquare()
    venues = fs.venues(lat, long, 10)
    for v in venues:
        print "Venue: ", v.name
        results = twitter_call(v.name, (lat,long,radius))
        for s in results:
            ht = parse_hashtags(s.text)
            for h in ht:
                if hashtags.has_key(h):
                    hashtags[h] = hashtags[h]+1
                else:
                    hashtags[h] = 1
    print hashtags
    return hashtags
    
def parse_hashtags(text):
    hashtags = []
    idx = text.find('#')
    while (idx != -1):
        hash = text[idx:].split()[0].lower().rstrip('!?. ')
        hashtags.append(hash)
        idx = text.find('#', idx+1)
    return hashtags

def good_tweets(hashtags):
    THRESHOLD = 10
    max = sorted(hashtags.iteritems(), key=lambda (k,v): (v,k), reverse=True)[0]
    good = []
    for tag in max:
        results = twitter_call(tag, None)
        good.extend(results)
        if len(good) > THRESHOLD:
            break
    for s in good:
        print s.user.screen_name, '\t', s.text, s.coordinates, s.location
        

if __name__ == '__main__':
    if len(sys.argv) > 2:
        good_tweets(popular_hashtags(float(sys.argv[1]), float(sys.argv[2])))
    else:
        good_tweets(popular_hashtags(cambridge_lat, cambridge_long))
