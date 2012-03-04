from datetime import datetime
from db import *
import time
import argparse
import sys
import os
import threading
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
    except KeyboardInterrupt:
        raise
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


class APIThread(threading.Thread):
    def __init__(self, apireader, dbpool):
        self.apireader = apireader
        self.dbpool = dbpool
        self.dead = False
        super(APIThread, self).__init__()

    def die(self):
        self.dead = True

    def run(self):
        reader = self.apireader
        while True:
            try:
                if not reader.should_scrape():
                    #print 'skipped ', reader.reader.name
                    time.sleep(1)
                    continue

                if self.dead:
                    break

                while True:
                    try:
                        db = self.dbpool.getconn()
                        break
                    except:
                        print "waiting for conn", self.reader.reader.name
                        time.sleep(1)



                nerrs, n = 0.0, 0.0
                for data in reader.reader:
                    n += 1
                    try:
                        eid, imgids = add_data(db, reader.reader.name, *data)
                        if eid is None:
                            nerrs += 1
                            # print >>sys.stderr, ( "Error with %s" % '\t'.join(map(str, data[:4])) )
                        else:
                            print "imported ", data[:4]
                    except KeyboardInterrupt:
                        raise
                    except:
                        nerrs += 1
                reader.update_timer(nerrs, n)

                self.dbpool.putconn(db)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print >>sys.stderr, "ERROR\t", reader.reader.name, '\t', e
                if isinstance(e, KeyboardInterrupt):
                    raise

            time.sleep(1)            


class APICron(threading.Thread):

    def __init__(self, dbname, dbpool):
        self.sources = [ PatchReader, InstagramReader, TwitterReader,
                         FoursquareVenueReader, YelpReader]
        self.threads = []
        self.dbpool = dbpool
        self.db = connect(dbname)
        super(APICron, self).__init__()

    def add_source(self, lat, lon):
        print "ADDING SOURCE", lat, lon
        for source in self.sources:
            newreader = APIReader(source(lat, lon))
            newthread = APIThread(newreader, self.dbpool)
            self.threads.append(newthread)
            newthread.start()

    def check_queries(self, first):
        if first:
            try:
                toadd = [row for row in query(self.db, 'select id, lat, lon from scrapers;')]
                for id, lat, lon in toadd:
                    self.add_source(lat, lon)
                self.db.commit()
            except Exception as e:
                print "check_queries error", e

        
        try:
            toadd = [row for row in query(self.db, 'select id, lat, lon from pendingqs')]
            for id, lat, lon in toadd:
                self.add_source(lat, lon)
                prepare(self.db, 'delete from pendingqs where id = %s', (id,), commit=False)
                prepare(self.db, 'insert into scrapers values (DEFAULT, %s, %s, %s)', (lat, lon, 0.5), commit=False)
                self.db.commit()
        except Exception as e:
            print 'check_queries error', e

    def die(self):
        for t in self.threads:
            t.die()
        self.dbpool.closeall()
        
    def run(self):
        now = datetime.now()
        first = True
        while True:
            try:
                # check to see if i should add scrapers
                self.check_queries(first)
                first = False
                time.sleep(1)
            except KeyboardInterrupt:
                self.die()
                break




if __name__ == '__main__':

    import psycopg2.pool
    dbpool = createpool(DBNAME)

    cron = APICron(DBNAME, dbpool)
    
    #cron.add_source(lat, lon)
    cron.start()

