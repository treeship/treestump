from flask import Flask, url_for, request
import tweets
import foursquare
#import patch  # this doesn't work because I can't install readability?

# python server.py
# Super hacky lightweight server which outputs data

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/tweets")
def show_tweets():
    lat = float(request.args['lat'])
    long = float(request.args['long'])
    out = "<html><body>"
    twits,popular = tweets.good_tweets(tweets.popular_hashtags(lat, long))
    for t in twits:
        out += "User: %s %s <br>" % (t.user.screen_name, t.text)
    for ht in popular:
        out += "Hashtag: %s Count: %d<br>" % (ht[0], ht[1])
    out+="</body></html>"
    return out

@app.route("/venues")
def show_venues():
    lat = float(request.args['lat'])
    long = float(request.args['long'])
    out = "<html><body>"
    fs = foursquare.Foursquare()
    venues = fs.venues(lat, long, 10)
    for v in venues:
        out += "Name: %s Location: %s <br>" % (v.name, v.location)
    out+="</body></html>"
    return out

@app.route("/stories")
def show_stories():
    lat = float(request.args['lat'])
    long = float(request.args['long'])
    out = "<html><body>"
    reader = PatchReader(lat, long)
    venues = fs.venues(lat, long, 10)
    while count < 100:
        for data in reader:
            out += "%s %s<br>" % (data[3], data[4])
    out+="</body></html>"
    return out
    
if __name__ == "__main__":
    app.run(debug=True)
