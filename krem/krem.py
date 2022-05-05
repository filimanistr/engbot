# -*- coding: utf-8 -*-

# ---Dmitrij edit---
# Python 3.7.3

import asyncio
import aiohttp
import requests
from configparser import ConfigParser

from aionuts import Bot, types, start_polling
from aionuts.types import Message, InlineKeyboard

import lang
from config import *

config = ConfigParser()
config.read('conf.cfg')
id = config['DEFAULT']['id']
token = config['DEFAULT']['token']
dictionary = lang.Dictionary() # Empty

bot = Bot(token, id)

@bot.message_handler(commands='help', prefixes='krem')
async def help(message):
    await message.answer(Messages.HELP)

@bot.message_handler(commands='d', prefixes='krem')
async def define(message):
    text = message.get_args()
    if text == '':
        text = 'Nothing to define'
        await message.answer(text)
        return True

    d = 'collins'
    text = text.split()
    if len(text) > 1:
        if text[-1] in dictionary.dictionaries.keys():
            d = text[-1]
            text = text[:-1]

    word = ' '.join(text)
    definition = await dictionary.define(word, d)
    await message.answer(definition)

@bot.message_handler(commands='ds', prefixes='krem')
async def ddefine(message):
    text = message.get_args()
    if text == '':
        text = 'Nothing to define'
        await message.answer(text)
        return True

    d = 'collins'
    text = text.split()
    if len(text) > 1:
        if text[-1] in dictionary.dictionaries.keys():
            d = text[-1]
            text = text[:-1]

    word = ' '.join(text)
    definition = await dictionary.define(word, d, detailed=True)
    await message.answer(definition)


@bot.message_handler(commands='s', prefixes='krem')
async def send_synonyms(message):
    text = message.get_args()
    if text == '': response = 'Where is the word?'
    else: response = await dictionary.get_synonyms(text)
    await message.answer(response)

@bot.message_handler(commands='t', prefixes='krem')
async def translate(message):
    text = message.get_args()
    if text == '': response = 'А что переводить?'
    else: response = await dictionary.translate(text, 'en')
    await message.answer(response)

@bot.message_handler(commands='td', prefixes='krem')
async def translated(message):
    text = message.get_args()
    if text == '': response = 'А что переводить?'
    else: response = await dictionary.translate(text, 'de')
    await message.answer(response)


async def main():
    await dictionary.write() # Fill it

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    start_polling(bot, loop=loop)
