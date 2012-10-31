# -*- coding: utf-8 -*-
__author__ = 'livelazily'

from datetime import datetime
from urlparse import urljoin

from lxml import etree
from models import GAEProxy
from google.appengine.ext import db
from google.appengine.api import mail

def getLastFile():
    url = "http://code.google.com/p/gaeproxy/downloads/list?can=2&q=&colspec=Filename"
    try:
        root = etree.parse(url, parser=etree.HTMLParser())
        cols = root.xpath('//*[@id="resultstable"]/tr[1]/td')
        file_link = cols[1].find('a')
        file_name = file_link.text.strip()
        detial_url = urljoin(url, file_link.get('href'))
        return file_name, detial_url
    except Exception as e:
        print(e)
        return '', ''


def getDetialData(url):
    """"""
    try:
        root = etree.parse(url, parser=etree.HTMLParser())
        rows = root.xpath('//*[@id="color_control"]/table/tbody/tr/td[2]/table/tr')

        file_link = rows[0].find('td/div/div[4]/a[1]').get('href')
        file_link = db.Link(urljoin(url,file_link))
        sha1 = rows[2].find('td').text
        desc = rows[1].find('td/pre').text
        return {'url': file_link, 'sha1': sha1, 'desc': desc, 'date': datetime.now()}
    except Exception as e:
        print(e)
        return {}


def sendEmail(name,link):
    message = mail.EmailMessage()

    message.sender = 'livelazily@gmail.com'
    message.to = 'livelazily@gmail.com'
    message.subject = u'GAEProxy 有新的版本 %s' % name
    message.body = u'''GAEProxy 有新的版本 %s 可以下载了
    下载地址为 %s
    ''' % (name,link)

    message.send()



if __name__ == "__main__":
    file_name, detial_url = getLastFile()
    if file_name:
        query = db.GqlQuery('SELECT * FROM GAEProxy WHERE name = :1', file_name)
        old_gae = query.get()
        if not old_gae:
            data = getDetialData(detial_url)
            new_gae = GAEProxy(name=file_name, **data)
            key = new_gae.put()
            sendEmail(file_name,data['url'])
            print('new gae file key is %s' % str(key.id_or_name()))
        else:
            key = old_gae.key()
            print('old gae file key is %s' % str(key.id_or_name()))
    print('<br> %s' % file_name)
