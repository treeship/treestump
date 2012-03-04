#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import Greenlet, sleep
from gevent.queue import Queue
from gevent.pywsgi import WSGIServer # must be pywsgi to support websocket
from geventwebsocket.handler import WebSocketHandler
from flask import Flask, request, render_template

import sys, os
sys.path.append( os.path.join(os.path.dirname(__file__), '..') )
from backend import szymon

import uuid
import simplejson
from datetime import datetime, timedelta

app = Flask(__name__)

DG = szymon.DataGatherer(None)

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
    self.greenlet = Greenlet(Publisher.serve, self)
    self.greenlet.start()
    # ask for data from the last minute
    self.query_time = None # datetime.now() - timedelta(minutes = 1)

  def serve(self):
    while self.subs:
      data = self.scrape()
      for s in self.subs:
        s.queue.put(data)
    # remove self
    del Publisher.pubs[self.key]

  def scrape(self):
    ## Fetch the data for that self.key.
    while True:
      data, next_time = DG.query(self.key[0],
                                 self.key[1],
                                 1.0,
                                 self.query_time)
      if data:
        break
      sleep(0.1) # wait for data for 100ms
    self.query_time = next_time
    # convert to primitive types for simplejson
    for d in data:
      d['time'] = str(d['time'])
    data = simplejson.dumps(data)
    return data


class Subscriber(object):
  def __init__(self, websocket):
    app.logger.debug("New Subscriber: %s", websocket)
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

  def serve(self):
    try:
      while True:
        request = self.websocket.receive()
        if request is None:
          break
        self.handle_request(request)
    except Exception, e:
      app.logger.error('An error occoured', exc_info=e)
    self.close()

  def handle_request(self, request):
    ## Take the key and map it to (possibly a set of) key(s).
    ## This will spawn publishers (scrapers) as required.
    try:
      location = simplejson.loads(request)
      # Key is (latitude, longitude) tuple
      # TODO: round-off location so that it's less precise
      key = (location['lat'], location['lng'])
    except:
      app.logger.error('Unrecognized request: %s' % request)
      print dir(request)
      return

    Publisher.register(key, self)

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/query')
def query():
  if request.environ.get('wsgi.websocket'):
    websocket = request.environ['wsgi.websocket']
    sub = Subscriber(websocket)
    sub.serve()
  return "bai"

if __name__ == '__main__':
  app.debug = True
  address = ('', 8080)
  http_server = WSGIServer(address, app, handler_class=WebSocketHandler)
  print "Listening on", address
  http_server.serve_forever()
