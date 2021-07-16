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
        if language.lan['lang']  == 'en':
            response = language.translator.translate(self.text, dest='ru').__dict__()
            return "%s - %s"%(self.text, response['text'])
        if language.lan['lang'] == 'ru':
            response = language.translator.translate(self.text, dest='en').__dict__()
            return "%s - %s"%(self.text, response['text'])
        return "Use an english or russian language for translate"

    def define(self):
        """ Parses the first definition from Collins dictionary, and returns string with it """
        if language.lan['lang']  == 'en':
            site = 'https://www.collinsdictionary.com/dictionary/english/%s'%(self.text)
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'none', 'Accept-Language': 'en-US,en;q=0.8', 'Connection': 'keep-alive'}
            # Downoad html page
            r = urllib.request.Request(site, headers = headers)
            html = urllib.request.urlopen(r).read()
            # pass html to bs4
            soup = BeautifulSoup(html, 'lxml')

            word_type = soup.find('span', class_='gramGrp pos').text
            definition = soup.find('div', class_='def').text
            response = '%s (%s) - %s'%(self.text, word_type, definition)
            return response
        return "Use an english words only"

    def fdefine(self):
        """ Parses all definitions from Collins dictionary, and returns string with all of them """
        if language.lan['lang']  == 'en':
            site = 'https://www.collinsdictionary.com/dictionary/english/%s'%(self.text)
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'none', 'Accept-Language': 'en-US,en;q=0.8', 'Connection': 'keep-alive'}
            # Downoad html page
            r = urllib.request.Request(site, headers = headers)
            html = urllib.request.urlopen(r).read()
            # pass html to bs4
            soup = BeautifulSoup(html, 'lxml')

            # Element with all definitions
            alld = soup.find('div', class_="content definitions cobuild br")

            # All grammar forms
            gp = []
            for response in alld.find_all('span', class_=['gramGrp pos', 'gramGrp']):
                gp.append(response.text)

            # All definitions
            d = []
            for response in alld.find_all('div', class_='def'):
                d.append(response.text)

            response = '%s\n\n'%(self.text.capitalize())
            for i in range(len(gp)):
                response+='%s. %s\n%s\n'%(i+1, gp[i].capitalize(), d[i].capitalize())

            return response.rstrip()
        return "Use an english words only"

    def pron(self):
        """ Downloading mp3 pronunciation of word, and returns bytes of it """
        if language.lan['lang']  == 'en':
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
