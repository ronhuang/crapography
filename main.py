#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#




import wsgiref.handlers


import os
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson
from google.appengine.ext import db


class Crap(db.Model):

  uid = db.StringProperty()
  cid = db.StringProperty()
  location = db.StringProperty()
  lat = db.FloatProperty()
  lng = db.FloatProperty()


class MainHandler(webapp.RequestHandler):

  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, {}))


class UserHandler(webapp.RequestHandler):

  def get(self, uid):
    if len(uid) == 0:
      self.redirect("/")
    else:
      template_values = {'uid': uid}
      path = os.path.join(os.path.dirname(__file__), 'user.html')
      self.response.out.write(template.render(path, template_values))


class UpdateHandler(webapp.RequestHandler):

  def post(self):
    uid = self.request.get('uid')
    cid = self.request.get('cid')
    lat = float(self.request.get('lat'))
    lng = float(self.request.get('lng'))
    location = self.request.get('location')

    craps = db.GqlQuery("SELECT * FROM Crap WHERE uid = :1 AND cid = :2", uid, cid)

    if craps.count() >= 1:
      for c in craps:
        c.lat = lat
        c.lng = lng
        c.location = location
        db.put(c)
    else:
      c = Crap(uid=uid, cid=cid, lat=lat, lng=lng, location=location)
      c.put()

    result = simplejson.dumps({'result': 'success'})
    self.response.out.write(result)


class RetrieveHandler(webapp.RequestHandler):

  def get(self, uid):
    craps = {}

    for c in db.GqlQuery("SELECT * FROM Crap WHERE uid = :1", uid):
      craps[c.cid] = {'location': c.location, 'lat': c.lat, 'lng': c.lng, 'cid': c.cid, 'uid': c.uid}

    self.response.out.write(simplejson.dumps(craps))


application = webapp.WSGIApplication([('/', MainHandler),
                                      (r'/user/(.*)', UserHandler),
                                      ('/update', UpdateHandler),
                                      ('/retrieve/(.*)', RetrieveHandler)],
                                     debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
