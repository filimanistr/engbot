# -*- coding: utf-8 -*-

# ---Lonely_Dark edit---
# Python 3.9.6

import requests

class vkapi:
    def __init__(self, token):
        self.token = token
        self.data = None
        self.update = {'v':'5.131', 'access_token': self.token}

    def get(self, method, params, paramsUp=1):
        if paramsUp:
            params.update(self.update)

        return requests.get(f"https://api.vk.com/method/{method}", params=params).json()

    def GetLP(self):
        self.data = requests.get("https://api.vk.com/method/groups.getLongPollServer", params={'group_id': '202800459', 'access_token': self.token, 'v': '5.131'}).json()

    def ListenLP(self):
       events = requests.get(self.data['response']['server'], params={'act': 'a_check', 'ts': self.data['response']['ts'], 'key': self.data['response']['key'], 'wait': 40}).json()
       
       if 'failed' in events:
        self.GetLP()
        return self.ListenLP()

       self.data['response']['ts'] = events['ts']
       return events['updates']
