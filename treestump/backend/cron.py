from datetime import datetime
from db import *
import time
import argparse
import sys
import os
sys.path.append( os.path.join(os.path.dirname(__file__), '..') )
from frontend.patch import PatchReader

# get_json(lat, lon, dist, newerthan_insertion_time) -> [ {} ]


DBNAME = 'angelhack'
EVENTINSERT = "insert into events values(DEFAULT, %s, %s, %s, %s, DEFAULT, %s, %s, %s) returning id"
IMGINSERT = "insert into events values(DEFAULT, %s, %s, %s) returning id"

deduphack = set()


# event
#  lat, lon, time, nonce, title, short, fulltxt, tag
# images
#  eventid, url, blob

def get_hash(*data, **kwargs):
    h = hash(data)
    return hash(data)
    

def add_data(db, tag, lat, lon, time, title, shorttxt, fulltxt, imgurls):
    hashval = get_hash(tag, lat, lon, title, shorttxt, fulltxt)
    print hashval
    params = (hashval, lat, lon, time, title, shorttxt, fulltxt)
    ret = prepare(db, EVENTINSERT, params = params)
    if ret is None: return None, None
    eid = ret[0]

    imgids = []
    for imgurl in imgurls:
        imgids.append( prepare(db, IMGINSERT, (eid, imgurl, None)) )
    return eid, imgids

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('lat')
    parser.add_argument('lon')
    parser.add_argument('db')
    args = parser.parse_args()

    lat, lon = float(args.lat), float(args.lon)

    sources = [ PatchReader ]
    readers = map(lambda s: s(lat, lon), sources)

    db = connect(args.db)

    try:
        while True:
            for reader in readers:
                for data in reader:
                    eid, imgids = add_data(db, reader.name, *data)
                    print "got eid", eid
            time.sleep(2)

    except KeyboardInterrupt:
        print "see ya!"



