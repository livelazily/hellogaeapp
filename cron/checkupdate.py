# -*- coding: utf-8 -*-
__author__ = 'livelazily'

import logging
from datetime import datetime
from urlparse import urljoin

from lxml import etree
from models import GAEProxy
from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api.urlfetch import fetch

def getLastFile():
    url = "https://code.google.com/p/gaeproxy/downloads/list?can=2&q=&colspec=Filename"
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


def getDetialData(url):
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


def sendEmail(name, data):
    message = mail.EmailMessage()
    message.sender = 'livelazily <livelazily@gmail.com>'
    message.to = 'livelazily@gmail.com'
    message.subject = u'GAEProxy 有新的版本 %s' % name
    message.body = u'''GAEProxy 有新的版本 %s 可以下载了
更新内容: %s
下载地址为: %s''' % (name, data.get('desc'),data.get('url'))
    message.send()


def checkUpdate():
    file_name, detial_url = getLastFile()
    if file_name:
        data = getDetialData(detial_url)
        query = db.GqlQuery('SELECT * FROM GAEProxy WHERE name = :1 and sha1 = :2', file_name, data.get('sha1'))
        old_gae = query.get()
        if not old_gae:
            new_gae = GAEProxy(name=file_name, **data)
            key = new_gae.put()
            sendEmail(file_name, data)
            print('new gae file key is %s' % str(key.id_or_name()))
        else:
            key = old_gae.key()
            print('old gae file key is %s' % str(key.id_or_name()))
    print('<br> %s' % file_name)


def main():
#    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(asctime)s %(message)s',
#                        datefmt='[%b %d %H:%M:%S]')
    logging.getLogger().setLevel(logging.DEBUG)
    try:
        checkUpdate()
    except Exception, e:
        logging.exception(e)
        print("check new version of GAEProxy faild!")


if __name__ == "__main__":
    main()
