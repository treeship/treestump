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
        if imgurls is None:
            imgurls = []
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
    from datetime import datetime, timedelta

    parser = argparse.ArgumentParser()
    parser.add_argument('lat')
    parser.add_argument('lon')
    parser.add_argument('db')
    args = parser.parse_args()

    lat, lon = float(args.lat), float(args.lon)

    MINDELAY = 2
    sources = [ PatchReader, InstagramReader, TwitterReader,
                FoursquareVenueReader, YelpReader]
    readers = dict( map(lambda s: (s(lat, lon), (MINDELAY, datetime.now())), sources) )
    

    db = connect(args.db)

    try:
        while True:
            now = datetime.now()
            for reader, (delay, nexttime) in readers.items():
                if nexttime > now:
                    print "skipped", now, nexttime
                    continue
                
                try:
                    nerrs, n = 0.0, 0.0
                    for data in reader:
                        n += 1
                        try:
                            eid, imgids = add_data(db, reader.name, *data)
                            if eid is None:
                                nerrs += 1
                                raise Exception( "Error with %s" % '\t'.join(map(str, data[:4])) )
                            else:
                                print "imported ", data[:4]
                        except Exception as e:
                            print >>sys.stderr, "ERROR\t", reader.name, '\t', e
                            pass

                    frac = nerrs / (n + 1.0)
                    if frac > 0.7:
                        delay *= 1.5
                    elif nerrs > 2:
                        delay = MINDELAY
                    readers[reader] = (delay, now + timedelta(seconds=delay) )
                    
                    print "DELAY", delay
                except Exception as e:
                    print >>sys.stderr, "ERROR\t", reader.name, '\t', e
            time.sleep(1)

    except KeyboardInterrupt:
        print "see ya!"



