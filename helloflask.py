# -*- coding: utf-8 -*-
__author__ = 'livelazily'

import logging

from flask import Flask

from cron import views

app = Flask(__name__)

app.config.update(
    DEBUG=True,
    SECRET_KEY='Dz@V3#u8eNwh2S^bioPfAa6gAT*1Ehd4'
)

logging.getLogger().setLevel(logging.DEBUG)

# url route
app.add_url_rule('/tasks/checkapp/', view_func=views.CheckGoogleCodeProjectUpdate.as_view('checkapp'))
app.add_url_rule('/tasks/', view_func=views.ShowTaskList.as_view('showtasks'))


@app.route('/')
def index():
    return 'Hello from Flask!\n'

