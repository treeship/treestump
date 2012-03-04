from instagram.client import InstagramAPI



class InstagramReader(object):

    def __init__(self, lat, lon):
        pass

    def next(self):
        pass


























access_token = "..."
api = InstagramAPI(access_token=access_token)
popular_media = api.media_popular(count=20)
for media in popular_media:
    print media.images['standard_resolution'].url    

