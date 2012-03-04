#
#

from db import *

RESTRICTED_KEYS = ['latlon', 'time', 'title', 'shorttxt', 'fulltxt', 'urls']

class DataGatherer(object):
    __mes__ = {}
    @staticmethod
    def instance(dbname):
        if dbname not in DataGatherer.__mes__:
            DataGatherer.__mes__[dbname] = DataGatherer(dbname)
        return DataGatherer.__mes__[dbname]

    def __init__(self, dbname):
        self.db = connect(dbname)

    def check_query(self, lat, lon, radius):
        params = (lat, lon, radius) 
        sql = "select count(*) from scrapers where (((lat - %s)^2) + ((lon - %s)^2))^0.5 < %s;"
        nhits = 0
        for row in query(self.db, sql, params):
            nhits +=  row[0]
        if nhits == 0:
            sql = "select count(*) from pendingqs where (((lat - %s)^2) + ((lon - %s)^2))^0.5 < %s;"
            nfound = 0
            for row in query(self.db, sql, params):
                nfound +=  row[0]
            if nfound == 0:
                print "ADDING PENDING QUERY"
                sql = "insert into pendingqs values (DEFAULT, %s, %s, %s);"
                prepare(self.db, sql, params=params, commit=True)
    

    def query(self, lat, lon, radius, min_insert_time, source=None):
        # check if scrapers exist
        self.check_query(lat, lon, radius)

        return self.run_query(lat, lon, radius, min_insert_time, source=None)


    def run_query(self, lat, lon, radius, min_insert_time, source=None):
        try:
            ret = []
            maxinstime = None
            for data in self.get_events(lat, lon, radius, min_insert_time, source):
                eid, source, lat, lon, time, lastinstime, title, shorttxt, fulltxt = data
                urls = self.get_imgs(eid)

                d = {'latlon': (lat, lon),
                     'source' : source,
                     'time' : time,
                     'title' : title,
                     'shorttxt' : shorttxt,
                     'fulltxt' : fulltxt,
                     'imgurls' : tuple(urls)}
                if maxinstime is None or maxinstime < lastinstime:
                    maxinstime = lastinstime

                md = self.get_metadata(eid)
                d.update(md)

                ret.append( d )
            return ret, maxinstime
        except Exception as e:
            print e
            return [], None

    def get_events(self, lat, lon, radius, min_insert_time, source):
        where = []
        params = []
        if lat and lon and radius:
            where.append( "(((lat - %s)^2) + ((lon - %s)^2))^0.5 < %s" )
            params.extend( (lat, lon, radius) )
        if min_insert_time:
            where.append( "addtime >= %s" )
            params.append(min_insert_time)
        if source:
            where.append( "source = %s" )
            params.append( source )

        sql = '''select id, source, lat, lon, time, addtime, title, shorttxt, fulltxt
        from events where %s
        order by addtime asc limit 30''' % ' and '.join(where)

        return [data for data in query(self.db, sql, params)]

    def get_imgs(self, eid):
        ret = []
        for url, blob in query(self.db, "select url, blob from imgs where eid = %s", (eid,)):
            ret.append( url )
        return ret

    def get_metadata(self, eid):
        ret = {}
        for key, val in query(self.db, "select key, val from metadata", (eid,)):
            ret[key] = val
        for banned in RESTRICTED_KEYS:
            if banned in ret:
                del ret[banned]
        return ret
        
        


if __name__ == '__main__':

    dg = DataGatherer('angelhack')
    for d in dg.query(40.740512, -73.991479, 1, None):
        print '\t', d.keys()
    for d in dg.query(40.740512, -73.991479, 1, None):
        print '\t', d.keys()
