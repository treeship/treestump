
# database setup

# if you don't have postgresql
sudo apt-get install postgresql
sudo su posgres
createuser <your username>
# tell it to allow create new databases

# once you have postgresql and user
createdb angelhack
psql -d angelhack -f treestump/ddl/create.ddl

# add to settings.py
DBUSER="<your username>"
DBPORT=<port of your postgresql, probably 5432>
DBNAME="angelhack"

# Running Cron

python cron.py

# Python libraries used

pip install django  # unless you already have it
pip install argparse
pip install requests
pip install python-twitter foursquare python-instagram

# readability is from github:
git clone git://github.com/gfxmonk/python-readability.git
cd python-readability
python setup.py install

http://code.google.com/p/python-twitter/
https://github.com/joet3ch/foursquare-python

# for pubsub.py
sudo apt-get install libevent-dev
pip install gevent gevent-websocket simplejson


##############
client protocol:

  query: {'lat': latitude, 'lng', longitutde }
  response: [ {'latlon': [lat, lon],
               'source' : source,
               'time' : time,
               'title' : title,
               'shorttxt' : shorttxt,
               'fulltxt' : fulltxt,
               'imgurls' : [url1, url2, ...] }, ... ]
