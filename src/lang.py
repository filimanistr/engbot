# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
import aiohttp
import json

from googletrans import Translator
from config import *


@dataclass
class Word:
    """Class that contains info about a word: definition,
    definition number, grammar_phorm and so on"""
    num: int
    word: str
    definition: str
    grammar_phorm: Optional[str] = ""
    example: Optional[str] = None
    synonyms: Optional[list[str]] = None
    antonyms: Optional[list[str]] = None


def format_output(pattern, word):
    """Formats string `pattern` that should contain {}
    by placing Word object's attibutes inside them."""
    response = "";
    response += pattern.format(
            num = word.num,
            word = word.word.capitalize(),
            grammar_phorm = word.grammar_phorm.capitalize(),
            definition = word.definition.capitalize(),
            example = word.example)
    return response.replace('[' ,'').replace(']' ,'')


class Collins:
    async def get_word(self, text):
        """Gets definitions of a word by parsing data from Collins website
        returns list of an Word objects"""
        url = f'{COLLINS_DICTIONARY_URL}/{text.replace(" ", "-")}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS) as ret:
                html = await ret.read()

        all_definitions = list()
        soup = BeautifulSoup(html, 'lxml')
        definitions = soup.find('div', class_=[
                "content definitions cobuild br",
                "content definitions ced",
                "content definitions american"])

        if definitions is None:
            return None

        for definition in definitions.find_all('div', class_='hom'):
            all_definitions.append(definition)

        words = list()
        for definition in all_definitions:
            phorm = definition.find('span', class_=['gramGrp pos', 'gramGrp'])
            defin = definition.find('div', class_='def')
            syn = definition.find('div', class_='thes')
            if None in (phorm, defin):
                break

            gp = phorm.text.strip()
            d = defin.text.strip()
            if syn == None:
                s = None
            else:
                s = [s.text for s in syn.find_all('a', class_='form ref')]
            i = all_definitions.index(definition)+1
            words.append(Word(num=i,
                              word=text,
                              grammar_phorm=gp,
                              definition=d,
                              synonyms=s))
        return words

    async def define(self, word):
        """Recieves the definitions of the given word
        and then formats them into output message"""
        data = await self.get_word(word)
        if data is None:
            return "Unknown word"

        response = format_output(DEFINITION_MESSAGE_PATTERN, data[0])
        if data[0].synonyms is not None:
            synonyms = ', '.join(data[0].synonyms)
            response += f'Synonyms: {synonyms}\n\n'
        return response

    async def defines(self, text):
        """Recieves the definitions of the given word
        and then formats them into output message
        (have the same purpose as the above method)"""
        data = await self.get_word(text)
        if data is None:
            return "Unknown word"

        response = f'{text.capitalize()}\n\n'
        for word in data:
            response += format_output(DEFINITIONS_MESSAGE_PATTERN, word)
            response += '\n'
        return response


class Urban:
    async def get_word(self, text):
        """Gets definitions of a word from the Urban website
        returns list of an Word objects"""
        url = f'{URBAN_DICTIONARY_URL}define?term={text.replace(" ", "%20")}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as ret:
                response = await ret.read()

        words = list()
        data = json.loads(response.decode('utf-8'))
        if not data['list']:
            return None

        for definition in data['list']:
            words.append(Word(word = text,
                              num = data['list'].index(definition)+1,
                              definition = definition['definition'],
                              example = definition['example']))
        return words

    async def define(self, text):
        """Recieves the definitions of the given word
        and then formats them into output message"""
        data = await self.get_word(text)
        if data is None:
            return 'Unknown word'
        return format_output(URBAN_DEFINITION_MESSAGE_PATTERN, data[0])

    async def defines(self, text):
        """Recieves the definitions of the given word
        and then formats them into output message
        (have the same purpose as the above method)"""
        data = await self.get_word(text)
        if data is None:
            return 'Unknown word'

        response = f'{text.capitalize()}\n\n'
        for word in data:
            response += format_output(URBAN_DEFINITIONS_MESSAGE_PATTERN, word)
            response += '-----------------------------------\n\n'
        return response


class Dictionary:
    def __init__(self):
        self.translator = Translator()
        self.collins = Collins()
        self.urban = Urban()
        self.dictionaries = ['collins', 'urban']

    async def translate(self, text, lang):
        '''Translates text and returns it'''
        language = self.translator.detect(text).__dict__
        inlang = language['lang']
        if inlang != 'ru': outlang = 'ru'
        else: outlang = lang;
        response = self.translator.translate(text, dest=outlang).__dict__()
        return response['text']

    async def get_synonyms(self, text):
        '''Returns all synonyms of the word'''
        data = await self.collins.get_word(text)
        if data is None:
            return "Unknown word"

        synonyms = list()
        for word in data:
            if word.synonyms is not None:
                synonyms += word.synonyms

        if not synonyms:
            return f"There isn't any synonyms for {text}"

        synonyms = ', '.join(set(synonyms))
        return f'Synonyms for {text}: {synonyms}'

