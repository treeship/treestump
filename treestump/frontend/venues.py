#!/usr/bin/python

import foursquare
import simplejson
import urllib2
from settings import *

class Venue:
    def __init__(self, item):
        self.name = item['name']
        self.location = item['location']
        self.id = item['id']
        self.categories = item['categories']

class Foursquare:
    API_URL="https://api.foursquare.com/v2/"
    VENUES_HANDLER="venues/search?"
    BASE_URL = API_URL+VENUES_HANDLER+"client_id="+FS_CLIENT_ID+"&client_secret="+FS_CLIENT_SECRET

    def venues(self, lat, long, num_results=10):
        if num_results > 50:
            print "50 is the limit"
            return
        url = self.BASE_URL + "&ll=%02f,%02f&intent=checkin&radius=500&limit=%d" % (lat, long, num_results)
        x = urllib2.urlopen(url).read()
        results = simplejson.loads(x)['response']['groups'][0]['items']
        k = []
        for i in results:
            v = Venue(i)
            k.append(v)
        return k

if __name__ == "__main__":
    fs = Foursquare()
    venues = fs.venues(42.363, -71.084, 10)
    for v in venues:
        print v.name
