from flask import Flask
app = Flask(__name__)
import tweets


@app.route("/")
def hello():
    out = ""
    twits,popular = tweets.run()
    for t in twits:
        out += "User: %s\t %s \n" % (t.user.screen_name, t.text)
    for ht in popular:
        out += "Hashtag: %s Count: %d\n" % (ht[0], ht[1])
    return out

if __name__ == "__main__":
    print hello()
    exit(1)
    app.run()
