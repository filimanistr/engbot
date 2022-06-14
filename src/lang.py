# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import asyncio
import aiohttp
import json

from googletrans import Translator


class Scrapper:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none', 'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        }

    async def get_session(self):
        self.session = aiohttp.ClientSession(headers = self.headers)
        return self.session

class Collins:
    def __init__(self):
        self.url = 'https://www.collinsdictionary.com/dictionary/english'

    async def get_word(self, text):
        url = f'{self.url}/{text.replace(" ", "-")}'
        async with self.session.get(url) as ret:
            html = await ret.read()

        # pass html to bs4
        soup = BeautifulSoup(html, 'lxml')
        # Element with all definitions
        alld = soup.find('div', class_=["content definitions cobuild br", "content definitions ced"])
        # list of certain blocks with definition
        ad = []
        for block in alld.find_all('div', class_='hom'):
            ad.append(block)

        gp = [] # All grammar pforms
        d = [] # All definitions
        s = [] # All synonyms
        for i in range(len(ad)):
            phorm = ad[i].find('span', class_=['gramGrp pos', 'gramGrp'])
            if phorm != None: gp.append(phorm.text)

            defin = ad[i].find('div', class_='def')
            if defin != None: d.append(defin.text)

            s.append([])
            syn = ad[i].find('div', class_='thes')
            if syn != None:
                for synonym in syn.find_all('a', class_='form ref'):
                    s[i].append(synonym.text)

        m = {'word': text, 'gp':gp, 'd':d, 's':s}
        return m

    async def define(self, text):
        try: data = await self.get_word(text)
        except: return "Try another word"

        response = '%s (%s) - %s'%(data['word'].capitalize(), data['gp'][0], data['d'][0])
        if data['s'][0] != []:
            syn = ', '.join(data['s'][0])
            synonyms = 'Synonyms: %s'%(syn)
            response+=synonyms

        return response.rstrip()

    async def defines(self, text):
        try: data = await self.get_word(text)
        except: return "Try another word"
        if data == None: return "Что то создает скриптовые ошибки"

        response = f'{text.capitalize()}\n\n'
        for i in range(len(data['gp'])):
            response+='%s. %s\n%s'%(i+1, data['gp'][i].capitalize(), data['d'][i].capitalize())
            if data['s'][i] != []:
                syn = ', '.join(data['s'][i])
                response+='Synonyms: %s'%(syn)
                response+='\n'
            response+='\n'

        return response.rstrip().replace('[' ,'').replace(']' ,'')

class Urban:
    def __init__(self):
        self.url = 'https://api.urbandictionary.com/v0/'

    async def get_word(self, text):
        url = f'{self.url}define?term={text.replace(" ", "%20")}'
        async with self.session.get(url) as ret:
            response = await ret.read()

        return json.loads(response.decode('utf-8'))

    async def define(self, text):
        try: data = await self.get_word(text)
        except: return "Try another word"

        for i in range(len(data['list'])):
            if data['list'][i]['word'].lower() == text:
                definition = data['list'][0]['definition']
                example = data['list'][0]['example']
                break

        try: response = f'{text.capitalize()} - {definition}\n\nExamples: {example}'.replace('[' ,'').replace(']' ,'')
        except: response = 'Что то создает скриптовые ошибки'
        return response.rstrip()

    async def defines(self, text):
        try: data = await self.get_word(text)
        except: return "Try another word"
        if data == None: return "Что то создает скриптовые ошибки"

        response = "%s\n\n"%(text.capitalize())
        for i in range(len(data['list'])):
            defin = data['list'][i]['definition']
            example = data['list'][i]['example']
            response+="Definition:\n%s\nExample:\n%s\n\n"%(defin, example)
            response+='-----------------------------------\n\n'

        return response.rstrip().replace('[' ,'').replace(']' ,'')

class Dictionary:
    translator = Translator()

    def __init__(self):
        self.collins = Collins()
        self.urban = Urban()
        self.dictionaries = {'collins':self.collins,
                             'urban':self.urban}

    async def write(self):
        '''Get session to request dicts'''
        self.scrapper = Scrapper()
        session = await self.scrapper.get_session()
        self.collins.session = session
        self.urban.session = session

    async def destroy(self):
        await self.collins.session.close()
        await self.urban.session.close()

    async def translate(self, text, lang):
        '''Translates text and returns it'''
        language = Dictionary.translator.detect(text).__dict__
        inlang = language['lang']
        if inlang != 'ru': outlang = 'ru'
        else: outlang = lang;
        response = Dictionary.translator.translate(text, dest=outlang).__dict__()
        return response['text']

    async def define(self, text, dictionary, detailed=False):
        '''Gets definition depending on dictionary and 'amount' of output'''
        if dictionary in self.dictionaries:
            if detailed:
                return await self.dictionaries[dictionary].defines(text)
            return await self.dictionaries[dictionary].define(text)
        return 'Unknown dictionary'

    async def get_synonyms(self, text):
        '''Gets synonyms of word'''
        try: data = await self.collins.get_word(text)
        except: return "Try another word"
        if data == None: return "Use english words only"

        top = f'Synonyms for {text}: '
        words = [word for words in data['s'] for word in words]
        if words == []:
            return f"There isn any synonyms for {text}"

        synonyms = ', '.join(set(words))
        return top + synonyms

