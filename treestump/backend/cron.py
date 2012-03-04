from datetime import datetime
from db import *
import time
import argparse
import sys
import os
sys.path.append( os.path.join(os.path.dirname(__file__), '..') )

# get_json(lat, lon, dist, newerthan_insertion_time) -> [ {} ]


DBNAME = 'angelhack'
EVENTINSERT = "insert into events values(DEFAULT, %s, %s, %s, %s, %s, DEFAULT, %s, %s, %s) returning id"
IMGINSERT = "insert into imgs values(DEFAULT, %s, %s, %s) returning id"
MDINSERT = "insert into metadata values (DEFAULT, %s, %s, %s) returning id"
deduphack = set()


# event
#  lat, lon, time, nonce, title, short, fulltxt, tag
# images
#  eventid, url, blob

def get_hash(*data, **kwargs):
    h = hash(data)
    return hash(data)
    

def add_data(db, tag, lat, lon, time, title, shorttxt, fulltxt, imgurls, metadata={}):
    try:
        hashval = get_hash(tag, lat, lon, title, shorttxt, fulltxt)
        params = (hashval, tag, lat, lon, time, title, shorttxt, fulltxt)
        ret = prepare(db, EVENTINSERT, params = params, commit=False)
        if ret is None: return None, None
        eid = ret[0]

        imgids = []
        for imgurl in imgurls:
            imgid = prepare(db, IMGINSERT, (eid, imgurl, None), commit=False)
            if imgid:
                imgids.append( imgid )
        mdids = []
        for key, val in metadata.items():
            mid = prepare(db, MDINSERT, (eid, key, val), commit=False)
            if mid:
                mdids.append( mid )

        db.commit()
        return eid, imgids
    except:
        return None, None

if __name__ == '__main__':
    from scrapers.patch import PatchReader
    from scrapers.instagramreader import InstagramReader
    from scrapers.tweets import TwitterReader
    from scrapers.foursquare import FoursquareVenueReader
    from scrapers.yelp import YelpReader

    parser = argparse.ArgumentParser()
    parser.add_argument('lat')
    parser.add_argument('lon')
    parser.add_argument('db')
    args = parser.parse_args()

    lat, lon = float(args.lat), float(args.lon)

    sources = [ PatchReader, InstagramReader, TwitterReader,
                FoursquareVenueReader, YelpReader]
    readers = map(lambda s: s(lat, lon), sources)

    db = connect(args.db)

    try:
        while True:
            for reader in readers:
                try:
                    for data in reader:
                        try:
                            eid, imgids = add_data(db, reader.name, *data)
                            if eid is None:
                                raise Exception( "Error with %s" % '\t'.join(map(str, data[:4])) )
                            else:
                                print "imported ", data[:4]
                        except Exception as e:
                            print >>sys.stderr, "ERROR\t", reader.name, '\t', e
                except Exception as e:
                    print >>sys.stderr, "ERROR\t", reader.name, '\t', e
            time.sleep(2)

    except KeyboardInterrupt:
        print "see ya!"



