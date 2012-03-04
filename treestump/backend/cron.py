from datetime import datetime
from db import *
import time
import argparse
import sys
import os
sys.path.append( os.path.join(os.path.dirname(__file__), '..') )
from settings import *

# get_json(lat, lon, dist, newerthan_insertion_time) -> [ {} ]


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


from scrapers.patch import PatchReader
from scrapers.instagramreader import InstagramReader
from scrapers.tweets import TwitterReader
from scrapers.foursquare import FoursquareVenueReader
from scrapers.yelp import YelpReader
from datetime import datetime, timedelta

class APIReader(object):
    MINDELAY = 2

    def __init__(self, reader):
        self.reader = reader
        self.delay = APIReader.MINDELAY
        self.nextscrape = datetime.now()

    def should_scrape(self):
        return self.nextscrape <= datetime.now()

    def update_timer(self, ndups, n):
        frac = float(ndups) / (n + 1.0)
        if frac > 0.7:
            self.delay *= 1.5
        elif (n-ndups) > 2:
            self.delay = APIReader.MINDELAY
        self.nextscrape = datetime.now() + timedelta(seconds=self.delay) 


class APICron(object):

    def __init__(self, dbname):
        self.sources = [ PatchReader, InstagramReader, TwitterReader,
                         FoursquareVenueReader, YelpReader]
        self.readers = []
        self.db = connect(dbname)

    def add_source(self, lat, lon):
        print "ADDING SOURCE", lat, lon
        for source in self.sources:
            self.readers.append(APIReader(source(lat, lon)))

    def check_queries(self):
        try:
            toadd = [row for row in query(self.db, 'select id, lat, lon from pendingqs')]
            for id, lat, lon in toadd:
                self.add_source(lat, lon)
                prepare(self.db, 'delete from pendingqs where id = %s', (id,), commit=False)
            commit=True
        except Exception as e:
            print 'check_queries error', e


    def run(self):
        # check to see if i should add scrapers
        self.check_queries()
        
        now = datetime.now()
        for reader in self.readers:
            if not reader.should_scrape():
                print 'skipped ', reader.reader.name
                continue

            try:
                
                nerrs, n = 0.0, 0.0
                for data in reader.reader:
                    n += 1
                    try:
                        eid, imgids = add_data(self.db, reader.reader.name, *data)

                        if eid is None:
                            nerrs += 1
                            print >>sys.stderr, ( "Error with %s" % '\t'.join(map(str, data[:4])) )
                        else:
                            print "imported ", data[:4]
                    except Exception as e:
                        print >>sys.stderr, "ERROR\t", reader.reader.name, '\t', e
                        pass

                reader.update_timer(nerrs, n)
                
            except Exception as e:
                print >>sys.stderr, "ERROR\t", reader.reader.name, '\t', e





if __name__ == '__main__':

    cron = APICron(DBNAME)
    #cron.add_source(lat, lon)
    try:
        while True:
            cron.run()
            time.sleep(1)
    except KeyboardInterrupt:
        print "see ya"
