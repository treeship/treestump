from db import *


class DataGatherer(object):
    __mes__ = {}
    @staticmethod
    def instance(dbname):
        if dbname not in DataGatherer.__mes__:
            DataGatherer.__mes__[dbname] = DataGatherer(dbname)
        return DataGatherer.__mes__[dbname]

    def __init__(self, dbname):
        self.db = connect(dbname)
    

    def query(self, lat, lon, radius, min_insert_time):
        ret = []
        for data in self.get_events(lat, lon, radius, min_insert_time):
            eid, lat, lon, time, title, shorttxt, fulltxt = data
            urls = self.get_imgs(eid)

            d = {'latlon': (lat, lon),
                 'time' : time,
                 'title' : title,
                 'shorttxt' : shorttxt,
                 'fulltxt' : fulltxt,
                 'urls' : tuple(urls)}
            ret.append( d )
        return ret

    def get_events(self, lat, lon, radius, min_insert_time):
        where = []
        params = []
        if lat and lon and radius:
            where.append( "(((lat - %s)^2) + ((lon - %s)^2))^0.5 < %s" )
            params.extend( (lat, lon, radius) )
        if min_insert_time:
            where.append( "addtime >= %s" )
            params.append(min_insert_time)

        sql = '''select id, lat, lon, time, title, shorttxt, fulltxt
        from events where %s
        order by addtime asc limit 30''' % ' and '.join(where)

        return [data for data in query(self.db, sql, params)]

    def get_imgs(self, eid):
        ret = []
        for url, blob in query(self.db, "select url, blob from imgs where eid = %s", (eid,)):
            ret.append( url )
        return ret
        
        


if __name__ == '__main__':

    dg = DataGatherer('angelhack')
    for d in dg.query(40.740512, -73.991479, 1, None):
        print d
