#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import Greenlet, sleep
from gevent.queue import Queue
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from flask import Flask, request, render_template

import uuid
import simplejson

app = Flask(__name__)

class Publisher(object):
  # maps key -> Publisher
  pubs = {}

  @staticmethod
  def register(key, sub):
    pub = Publisher.pubs.get(key, None)
    if pub is None:
      pub = Publisher(key, sub)
      Publisher.pubs[key] = pub
    else:
      pub.subs.add(sub)
    sub.pubs.add(pub)

  def __init__(self, key, sub):
    self.key = key
    self.subs = set([sub])
    self.greenlet = Greenlet(Publisher.scrape, self)
    self.greenlet.start()

  def scrape(self):
    while self.subs:
      ## TODO: take the key and fetch the data for that key
      ## for example from foursquare, twitter, etc.
      ## does not matter if it's blocking or not
      print "Publisher: %s scraping now" % self.key
      sleep(1)
      ## TODO: extract the data that should be pushed to the subscribers.
      data = "{{" + self.key + "--" + self.key + "}}"

      # optionally save data to db
      for s in self.subs:
        s.queue.put(data)
    # remove self
    del Publisher.pubs[self.key]

class Subscriber(object):
  def __init__(self, websocket):
    self.websocket = websocket
    self.pubs = set()
    self.queue = Queue(None) # infinite capacity
    self.greenlet = Greenlet(Subscriber.send_data, self)
    self.greenlet.start()

  def send_data(self):
    try:
      while True:
        # The subscriber sends back to the client "as is".
        data = self.queue.get()
        self.websocket.send(data)
    except Exception, e:
      app.logger.error('An error occoured', exc_info=e)
      self.close()

  def close(self):
    for p in self.pubs:
      p.subs.remove(self)

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/query')
def query():
  if request.environ.get('wsgi.websocket'):
    websocket = request.environ['wsgi.websocket']
    sub = Subscriber(websocket)
    app.logger.debug("New Subscriber: %s", websocket)
    try:
      while True:
        key = websocket.receive()
        if key is None:
          break
        ## TODO: take the key and map it to (possibly a set of) key(s).
        ## This will spawn publishers (scrapers) as required.
        key = str(key)
        Publisher.register(key, sub)
    except Exception, e:
      app.logger.error('An error occoured', exc_info=e)
    sub.close()
  return "bai"

if __name__ == '__main__':
  app.debug = True
  address = ('', 8080)
  http_server = WSGIServer(address, app, handler_class=WebSocketHandler)
  print "Listening on", address
  http_server.serve_forever()
