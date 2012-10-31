# -*- coding: utf-8 -*-
__author__ = 'livelazily'

from google.appengine.ext import db

class GAEProxy(db.Model):
    name = db.StringProperty(required=True)
    date = db.DateTimeProperty()
    sha1 = db.StringProperty()
    url = db.LinkProperty()
    desc = db.StringProperty(multiline=True)
