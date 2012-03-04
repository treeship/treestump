from instagram.client import *

import sys, os
sys.path.append( os.path.join(os.path.dirname(__file__), '../../') )
from settings import *





class InstagramReader(object):

    def __init__(self, lat, lon):
        self.lat, self.lon = lat, lon

    name = property(lambda self: 'Instagram')

    def next(self):
        access_token = INSTAGRAM_ACCESS_TOKEN
        api = InstagramAPI(access_token=access_token)
        #popular_media = api.media_popular(count=20)
        #api.location_search(lat=self.lat, lng=self.lon)
        nearby_media = api.media_search(lat=self.lat, lng=self.lon)
        for media in nearby_media:
            try:
                url = media.get_standard_resolution_url()
                user = media.user
                loc = media.location
                mlat, mlon = loc.point.latitude, loc.point.longitude
                time = media.created_time
                title = media.caption and media.caption.text or ''
                metadata = {'locname' : loc.name,
                            'likes' : media.like_count,
                            'filter' : media.filter,
                            'fullname' : user.full_name,
                            'userpic' : user.profile_picture}
                yield mlat, mlon, time, title, None, None, [url], metadata
            except:
                continue

    def __iter__(self):
        return self.next()







if __name__ == '__main__':

    lat, lon = 42.363, -71.084
    ireader = InstagramReader(lat, lon)
    for row in ireader:
        print row
