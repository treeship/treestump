#!/usr/bin/python

import twitter
import sys
from venues import Foursquare
from settings import *

cambridge_lat = 42.363
cambridge_long = -71.084
radius = '10mi'

def twitter_call(term, geo):
    api = twitter.Api(consumer_key, consumer_secret, access_token, access_secret)
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
            print s.user.screen_name, '\t', s.text, s.coordinates, s.location
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

if __name__ == '__main__':
    if len(sys.argv) > 2:
        popular_hashtags(float(sys.argv[1]), float(sys.argv[2]))
    else:
        popular_hashtags(cambridge_lat, cambridge_long)
