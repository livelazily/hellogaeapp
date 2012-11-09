# -*- coding: utf-8 -*-
from flask import render_template

__author__ = 'livelazily'

import logging

from flask.views import View
from urlparse import urljoin

from lxml import etree
from models import GAEProxy
from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api.urlfetch import fetch

class CheckGoogleCodeProjectUpdate(View):
    def dispatch_request(self):
        try:
            quert = db.GqlQuery('SELECT * FROM Task ORDER BY name')
            quert = quert.fetch(10)
            for task in quert:
                project_name = task.name
                self._checkUpdate(project_name)
        except Exception, e:
            logging.exception(e)
            return "check update faild!"
        return "Task not found!"


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
            sha1 = rows[2].find('td').text
            desc = rows[1].find('td/pre').text
            return {'url': file_link, 'sha1': sha1.strip(), 'desc': desc}
        except Exception as e:
            logging.exception(e)
            raise


    def _sendEmail(self, project_name, file_name, link):
        message = mail.EmailMessage()
        message.sender = 'livelazily <livelazily@gmail.com>'
        message.to = 'livelazily@gmail.com'
        message.subject = u'%s 有新的版本 %s' % (project_name, file_name)
        message.body = u'%s 有新的版本 %s 可以下载了\n下载地址为 %s' % (project_name, file_name, link)
        message.send()


    def _checkUpdate(self, project_name):
        file_name, detial_url = self._getLastFile(project_name)
        if file_name:
            data = self._getDetialData(detial_url)
            query = db.GqlQuery('SELECT * FROM GAEProxy WHERE name = :1 and sha1 = :2', file_name, data.get('sha1'))
            old_gae = query.get()
            if not old_gae:
                new_gae = GAEProxy(name=file_name, **data)
                key = new_gae.put()
                self._sendEmail(file_name, data['url'])
                print('new gae file key is %s' % str(key.id_or_name()))
            else:
                key = old_gae.key()
                print('old gae file key is %s' % str(key.id_or_name()))
        print('<br> %s' % file_name)


class ShowTaskList(View):
    def get_template_name(self):
        return 'index.html'

    def render_template(self, context):
        return render_template(self.get_template_name(), **context)

    def dispatch_request(self):
        context = {"task": "tasks"}
        return self.render_template(context)
