#-*- coding: utf-8
import requests
import json

class Mail():

    def __init__(self, subject, html):
        self.api_host = 'https://sendcloud.sohu.com/webapi'
        self.subject = subject
        self.html = html
        self.api_user = 'postmaster@devfry.sendcloud.org'
        self.api_key = 'wASu3IYkaTbO'

    def send(self, to, sender='devfry-noreply@bbwc.cn', sendername='DevFry'):
        url = self.api_host + '/mail.send.json'
        data = {
            'api_user': self.api_user,
            'api_key': self.api_key,
            'subject': self.subject,
            'html': self.html,
            'to': to
            'from': sender,
            'fromname': sendername,
            }
        result = json.loads(requests.post(url, data=data).content)
        return result
