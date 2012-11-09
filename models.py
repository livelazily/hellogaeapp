# -*- coding: utf-8 -*-
__author__ = 'livelazily'

from google.appengine.ext import db

class GAEProxy(db.Model):
    name = db.StringProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)
    sha1 = db.StringProperty()
    url = db.LinkProperty()
    desc = db.StringProperty(multiline=True)

class Task(db.Model):
    name = db.StringProperty(required=True)
    url = db.LinkProperty(required=True)
