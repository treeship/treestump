# Yelp Search API

import json
import oauth2
import optparse
import urllib
import urllib2
import time
from django.utils.encoding import smart_str
import datetime
import os, sys
sys.path.append( os.path.join(os.path.dirname(__file__), '../../') )
import settings
import argparse

# handles request and oauth signature
# returns parsed json
def request(host, path,
            url_params,
            consumer_key,
            consumer_secret,
            token,
            token_secret):
    """Returns response for API request."""
    # Unsigned URL
    encoded_params = ''
    if url_params:
        encoded_params = urllib.urlencode(url_params)
    url = 'http://%s%s?%s' % (host, path, encoded_params)
    # print 'URL: %s' % (url,)

    # Sign the URL
    consumer = oauth2.Consumer(consumer_key, consumer_secret)
    oauth_request = oauth2.Request('GET', url, {})
    oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),
                          'oauth_timestamp': oauth2.generate_timestamp(),
                          'oauth_token': token,
                          'oauth_consumer_key': consumer_key})

    token = oauth2.Token(token, token_secret)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(),
                               consumer, token)
    signed_url = oauth_request.to_url()
    # print 'Signed URL: %s\n' % (signed_url,)

    # Connect
    try:
        conn = urllib2.urlopen(signed_url, None)
        try:
            response = json.loads(conn.read())
        finally:
            conn.close()
    except urllib2.HTTPError, error:
        response = json.loads(error.read())

    return response

class YelpReader():

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    name = property(lambda self: 'Yelp')

    def next(self):
        ids = self.get_nearby_restaurants()

        reviews = []
        for i in ids:
            reviews.extend(self.get_reviews(i))

        for r in reviews:
            yield self.lat, self.lon, r[0], r[1], r[2], r[3], r[4]


    def get_nearby_restaurants(self):
        url_params = {}
        url_params['term'] = "restaurants"
        url_params['ll'] = "{0},{1}".format(self.lat, self.lon)
        url_params['limit'] = str(settings.YELP_RESULTS_LIMIT)
        url_params['radius_filter'] = "200"
        url_params['category_filter'] = "restaurants"
        url_params['sort'] = "0"
        # 0 for best matched
        # 1 for distance
        # 2 highest rated

        response = request(settings.YELP_HOST,
                           '/v2/search', # path
                           url_params,
                           settings.YELP_CONSUMER_KEY,
                           settings.YELP_CONSUMER_SECRET,
                           settings.YELP_TOKEN,
                           settings.YELP_TOKEN_SECRET)

        businesses = response['businesses']
        total = response['total']

        ids = []
        for b in businesses:
            #print b['id']
            ids.append(b['id'])

        return ids

    def get_reviews(self, business_id):

        url_params = {}
        i = smart_str(business_id)
        try:
            path = u"/v2/business/%s" % (smart_str(i, 'ascii'),)
        except Exception as e:
            print 'error', i
            return None

        try:
            response = request(settings.YELP_HOST,
                               path,
                               url_params,
                               settings.YELP_CONSUMER_KEY,
                               settings.YELP_CONSUMER_SECRET,
                               settings.YELP_TOKEN,
                               settings.YELP_TOKEN_SECRET)
        except Exception as e:
            return None
        reviews = response['reviews']

        #print '\n', 'Reviews for', response['name']

        parsed_reviews = []
        # datetime, title, short text, long/full text, list of image urls
        for r in reviews:
            title = response['name']
            short_text = r['user']['name']
            t = time.localtime(r['time_created'])
            date = datetime.datetime(t.tm_year,
                                     t.tm_mon,
                                     t.tm_mday,
                                     t.tm_hour,
                                     t.tm_min,
                                     t.tm_sec)
            full_text = r['excerpt']
#            print r['user']['name'], 'said on', t.tm_mon, t.tm_mday, t.tm_year, '...'
#            print r['excerpt']
            images = []
            if 'image_url' in response:
                images.append(response['image_url'])
            if 'user' in r and 'image_url' in r['user']:
                images.append( r['user']['image_url'] )
            parsed_reviews.append([date,
                                   title,
                                   short_text,
                                   full_text,
                                   images])
        return parsed_reviews

    def __iter__(self):
        return self.next()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('lat')
    parser.add_argument('lon')
    args = parser.parse_args()

    reader = YelpReader(args.lat, args.lon)
    try:
        for data in reader:
            print data
    except KeyboardInterrupt:
        pass

