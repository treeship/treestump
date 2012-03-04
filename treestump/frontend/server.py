from flask import Flask
app = Flask(__name__)
import tweets


@app.route("/")
def hello():
    out = "<html><body>"
    twits,popular = tweets.run()
    for t in twits:
        out += "User: %s %s <br>" % (t.user.screen_name, t.text)
    for ht in popular:
        out += "Hashtag: %s Count: %d<br>" % (ht[0], ht[1])
    out+="</body></html>"
    return out

if __name__ == "__main__":
    app.run()
