import requests, json
import asyncio

class vkapi:
    def __init__(self, token):
        self.token = token
        self.data = None

    def get(self, method, **kwargs):
        param = {'v':'5.131', 'access_token':self.token}
        param.update(kwargs)
        r = requests.post('https://api.vk.com/method/'+method, data=param)
        return json.loads(r.text)

    async def GetLP(self):
        r = requests.get('https://api.vk.com/method/groups.getLongPollServer?group_id=202800459&access_token=%s&v=5.131'%(self.token))
        self.data = json.loads(r.text)

    async def ListenLP(self):
        try:
            updates = requests.post('%s?act=a_check&key=%s&ts=%s&wait=25'%(self.data['response']['server'], self.data['response']['key'], self.data['response']['ts'])).json()
            # updates = json.loads(r.text)

            if 'failed' in updates:
                await self.GetLP()
                return await self.ListenLP()

            self.data['response']['ts'] = updates['ts']
            return updates['updates']

        except:
            await self.GetLP()
            return await self.ListenLP()
