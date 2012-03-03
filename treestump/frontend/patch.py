#!/usr/bin/env python2.7
from datetime import datetime
import urllib2
import argparse
import hashlib
import json
import sys
import time
import urllib
import requests
import os
from readability.readability import Document
from django.utils.encoding import smart_str, smart_unicode
sys.path.append( os.path.join(os.path.dirname(__file__), '..') )
from settings import *


# python test.py 40.740512 -73.991479

class StoryFinder:
    BASE_URL = 'http://hyperlocal-api.outside.in/v1.1'
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def find_stories(self, lat, lon):
        response = self.request("/nearby/%s,%s/stories" % (urllib.quote(str(lat)), urllib.quote(str(lon))))
        stories = json.loads(response.read())['stories']
        response.close()
        if len(stories) == 0:
            return []
        #raise Exception("NOTHING FOUND")
        else:
            return stories

    def request(self, path):
        url = self.sign("%s%s" % (StoryFinder.BASE_URL, path))
        #print "Requesting %s" % url
        response = urllib.urlopen(url)
        if response.getcode() == 200:
            return response
        else:
            raise Exception("Request failed with code %s" % (response.getcode()))

    def sign(self, url):
        sig = hashlib.md5(self.key + self.secret + str(int(time.time()))).hexdigest()
        return "%s?dev_key=%s&sig=%s" % (url, self.key, sig)



class PatchReader(object):
    def __init__(self, lat, lon):
        self.lat, self.lon = lat, lon

    name = property(lambda self: 'Patch')

    def extract_data(self, patchurl):
        try:
            f = requests.get(patchurl)
            html = f.content
            doc = Document(html)
            title = doc.short_title()
            summary = doc.summary()
            return smart_str(title), smart_str(summary)
        except:
            return None, None


    def next(self):
        stories = StoryFinder(PATCH_KEY, PATCH_SECRET).find_stories(self.lat, self.lon)
        for story in stories:
            try:
                title, summary = self.extract_data( story['story_url'] )
                yield self.lat, self.lon, datetime.now(), title, None, summary, []
            except Exception as e:
                print e
                pass
        raise StopIteration

    def __iter__(self):
        return self.next()
        class I(object):
            def next(self):
                return 
            def __iter__(self):
                return self
        return self
            

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('lat')
    parser.add_argument('lon')
    args = parser.parse_args()

    reader = PatchReader(args.lat, args.lon)
    try:
        while True:
            for data in reader:
                print data
    except KeyboardInterrupt:
        pass
