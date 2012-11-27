# -*- coding: utf-8 -*-
__author__ = 'livelazily'

import logging
import os

from google.appengine.api import mail
from google.appengine.api.app_identity import get_application_id
from google.appengine.api.urlfetch import fetch
from google.appengine.ext import db

from lxml import etree
from models import ProjectFile

from flask import render_template, render_template_string
from flask.views import View
from urlparse import urljoin

class CheckGoogleCodeProjectUpdate(View):
    def dispatch_request(self):
        file_msgs = []
        try:
            query = db.GqlQuery('SELECT * FROM Task')
            query = query.fetch(10)

            for task in query:
                project_name = task.name
                file_msgs.append(self._checkUpdate(project_name))
            if len(query) < 1:
                file_msgs.append("Task not found!")
        except Exception, e:
            logging.exception(e)
            return render_template_string('<div>Check update faild!</div>')
        logging.debug(file_msgs)
        return render_template('taskresult.jinja2', file_msgs=file_msgs)


    def _getLastFile(self, project_name):
        url = "https://code.google.com/p/%s/downloads/list?can=2&q=&colspec=Filename" % project_name
        try:
            root = etree.fromstring(fetch(url=url).content, parser=etree.HTMLParser())
            cols = root.xpath('//*[@id="resultstable"]/tr[1]/td')
            file_link = cols[1].find('a')
            file_name = file_link.text.strip()
            detial_url = urljoin(url, file_link.get('href'))
            return file_name, detial_url
        except Exception as e:
            logging.exception(e)
            raise


    def _getDetialData(self, url):
        try:
            root = etree.fromstring(fetch(url=url).content, parser=etree.HTMLParser())
            rows = root.xpath('//*[@id="color_control"]/table/tbody/tr/td[2]/table/tr')

            file_link = rows[0].find('td/div/div[4]/a[1]').get('href')
            file_link = db.Link(urljoin(url, file_link))
            sha1 = rows[2].find('td/span').text
            desc = rows[1].find('td/pre').text
            return {'url': file_link, 'sha1': sha1.strip(), 'desc': desc}
        except Exception as e:
            logging.exception(e)
            raise


    def _sendEmail(self, project_name, file_name, data):
        message = mail.EmailMessage()
        message.sender = 'task@%s.appspotmail.com' % get_application_id()
        message.to = 'livelazily@gmail.com'
        message.subject = u'%s 有新的版本 %s 可以下载了' % (project_name, file_name)
        message.body = u'''更新内容: %s
下载地址为: %s''' % (data.get('desc'), data.get('url'))

        message.send()


    def _checkUpdate(self, project_name):
        file_name, detial_url = self._getLastFile(project_name)
        file_msg = []
        if file_name:
            data = self._getDetialData(detial_url)
            query = db.GqlQuery('SELECT __key__ FROM ProjectFile WHERE name = :1 and sha1 = :2', file_name,
                                data.get('sha1'))
            old_file = query.get()
            if not old_file:
                new_file = ProjectFile(name=file_name, **data)
                key = new_file.put()
                self._sendEmail(project_name, file_name, data)
                file_msg.append('new gae file key is %s' % str(key.id_or_name()))
            else:
                key = old_file
                file_msg.append('old gae file key is %s' % str(key.id_or_name()))
        file_msg.append('<br> %s' % file_name)
        return "".join(file_msg)


class ShowTaskList(View):
    def get_template_name(self):
        return 'index.jinja2'

    def render_template(self, context):
        return render_template(self.get_template_name(), **context)

    def dispatch_request(self):
        tasks = db.GqlQuery('SELECT * FROM Task')
        tasks = tasks.fetch(10)

        server = os.environ.get("SERVER_SOFTWARE")
        version = os.environ.get("CURRENT_VERSION_ID")
        context = {"tasks": tasks, "server": server, "version": version}
        
        return self.render_template(context)
