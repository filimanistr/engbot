# -*- coding: utf-8 -*-

import urllib
import urllib.request
import requests
from bs4 import BeautifulSoup

from googletrans import Translator

class language:
    translator = Translator()
    lan = None

    def __init__(self, text):
        self.text = text
        language.lan = language.translator.detect(self.text).__dict__

    def translate(self):
        """ Translates text, returns string with it """
        if language.lan['lang'] == 'en':
            response = language.translator.translate(self.text, dest='ru').__dict__()
            return "%s - %s"%(self.text, response['text'])
        if language.lan['lang'] == 'ru':
            response = language.translator.translate(self.text, dest='en').__dict__()
            return "%s - %s"%(self.text, response['text'])
        return "Use an english or russian language for translate"

    def meaning(self):
        """ Parses all definitions from Collins dictionary, and returns string with all of them """
        if language.lan['lang'] == 'en':
            site = 'https://www.collinsdictionary.com/dictionary/english/%s'%(self.text)
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'none', 'Accept-Language': 'en-US,en;q=0.8', 'Connection': 'keep-alive'}
            # Downoad html page
            r = urllib.request.Request(site, headers = headers)
            html = urllib.request.urlopen(r).read()
            # pass html to bs4
            soup = BeautifulSoup(html, 'lxml')

            # Element with all definitions
            # alld = soup.find('div', class_="content definitions cobuild br")
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
            m = {'gp':gp, 'd':d, 's':s}
            return m
        return None

    def define(self):
        m = language.meaning(self)
        if m != None:
            response = '%s (%s) - %s'%(self.text.capitalize(), m['gp'][0], m['d'][0])
            if m['s'][0] != []:
                syn = ', '.join(m['s'][0])
                synonyms = 'Synonyms: %s'%(syn)
                response+=synonyms

            return response.rstrip()
        return "Use an english words only"

    def fdefine(self):
        m = language.meaning(self)
        if m != None:
            response = '%s\n\n'%(self.text.capitalize())
            for i in range(len(m['gp'])):
                response+='%s. %s\n%s'%(i+1, m['gp'][i].capitalize(), m['d'][i].capitalize())
                if m['s'][i] != []:
                    syn = ', '.join(m['s'][i])
                    response+='Synonyms: %s'%(syn)
                response+='\n\n'

            return response.rstrip()
        return "Use an english words only"

    def pron(self):
        """ Downloading mp3 pronunciation of word, and returns bytes of it """
        if language.lan['lang'] == 'en':
            site = 'https://www.collinsdictionary.com/dictionary/english/%s'%(self.text)
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'none', 'Accept-Language': 'en-US,en;q=0.8', 'Connection': 'keep-alive'}
            # Downoad html page
            r = urllib.request.Request(site, headers = headers)
            html = urllib.request.urlopen(r).read()
            # pass html to bs4
            soup = BeautifulSoup(html, 'lxml')

            # Element with all definitions
            pron = soup.find('span', class_="pron type-")
            link = pron.find('span', 'ptr hwd_sound type-hwd_sound').a['data-src-mp3']

            r = urllib.request.Request(link, headers = headers)
            sound = urllib.request.urlopen(r).read()
            return sound

        return "Use an english words only"

    def kfig(self):
        """ Translate russian to chinese and back. Returns the transkated word/sentence """
        if language.lan['lang'] == 'ru':
            response = language.translator.translate(self.text, dest='zh-CN').__dict__()
            return " %s"%(response['text'])
        if language.lan['lang'] == 'zh-CN':
            response = language.translator.translate(self.text, dest='ru').__dict__()
            return "%s"%(response['text'])
        return "Use only chineese or russian symbols"
