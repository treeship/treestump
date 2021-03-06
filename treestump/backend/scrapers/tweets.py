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
from foursquare import Foursquare
import os
sys.path.append( os.path.join(os.path.dirname(__file__), '../../') )
from settings import *

cambridge_lat = 42.363
cambridge_long = -71.084
radius = '10mi'


class TwitterReader:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    name = property(lambda self:"Twitter")

    def next(self):
        tt, x = good_tweets(popular_hashtags(self.lat, self.lon))
        tweets = list(tt)
        tweets.extend(local_tweets(self.lat, self.lon))
        for tweet in tweets:
            try:
                title = tweet.text
                time = tweet.GetCreatedAt()
                images = [] #images_from_tweet(tweet)
                yield self.lat, self.lon, time, title, tweet.text, None, extract_images(tweet)
            except Exception as e:
                print e
                pass
        raise StopIteration

    def __iter__(self):
        return self.next()
    
def extract_images(tweet):
    # TODO: Stupid python-twitter doesn't give me back entitities,
    # which might have more interesting urls in the tweet, parsed for
    # me.  Either parse the tweet for images or send the API call
    # directly so I can retrieve entitities.
    return [tweet.user.profile_image_url]

def get_api():
    api = twitter.Api(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, 
                      TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    return api

def twitter_call(term, geo):
    results = []
    api = get_api()
    try:
        results = api.GetSearch(term=term, geocode=geo)
    except Exception as e:
        print "GetSearch failed: ", term, geo, e
        pass
    return results

def popular_hashtags(lat, long):
    hashtags = {}
    fs = Foursquare()
    venues = fs.venues(lat, long, 10)
    for v in venues:
        #print "Venue: ", v.name
        results = twitter_call(v.name, (lat,long,radius))
        for s in results:
            ht = parse_hashtags(s.text)
            for h in ht:
                if hashtags.has_key(h):
                    hashtags[h] = hashtags[h]+1
                else:
                    hashtags[h] = 1
    return hashtags
    

def local_tweets(lat, long):
    tweets = twitter_call("the", (lat,long,radius))
    return tweets

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
    max = sorted(hashtags.iteritems(), key=lambda (k,v): (v,k), reverse=True)
    good = []
    for tag in max:
        results = twitter_call(tag[0], None)
        good.extend(results)
        if len(good) > THRESHOLD:
            break
    return good, max
        
def run():
    x, max = good_tweets(popular_hashtags(cambridge_lat, cambridge_long))
    for tweet in x:
        print tweet.user.screen_name, tweet.text
    return good_tweets(popular_hashtags(cambridge_lat, cambridge_long))

if __name__ == '__main__':
    if len(sys.argv) > 2:
        print good_tweets(popular_hashtags(float(sys.argv[1]), float(sys.argv[2])))
        print "LOCAL: "
        print local_tweets(float(sys.argv[1]), float(sys.argv[2]))
    else:
        print run()
