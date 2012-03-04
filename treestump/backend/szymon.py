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
    

    def query(self, lat, lon, radius, min_insert_time, source=None):
        try:
            ret = []
            for data in self.get_events(lat, lon, radius, min_insert_time, source):
                eid, source, lat, lon, time, title, shorttxt, fulltxt = data
                urls = self.get_imgs(eid)

                d = {'latlon': (lat, lon),
                     'source' : source,
                     'time' : time,
                     'title' : title,
                     'shorttxt' : shorttxt,
                     'fulltxt' : fulltxt,
                     'imgurls' : tuple(urls)}

                md = self.get_metadata(eid)
                d.update(md)

                ret.append( d )
            return ret
        except Exception as e:
            print e
            return []

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

        sql = '''select id, source, lat, lon, time, title, shorttxt, fulltxt
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
        print d
