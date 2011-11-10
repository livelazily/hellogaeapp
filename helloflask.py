# -*- coding: utf-8 -*-
__author__ = 'livelazily'


from flask import Flask
app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def index(anythingelse=''):
    return 'Hello %s from Flask!\n' % anythingelse

