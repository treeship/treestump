
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
DBUSER=<your username>
DBPORT=<port of your postgresql, probably 5432>

# Python libraries used

pip install readability
pip install requests
pip install python-twitter foursquare instagram

http://code.google.com/p/python-twitter/
https://github.com/joet3ch/foursquare-python

# for pubsub.py
sudo apt-get install libevent-dev
pip install gevent gevent-websocket

