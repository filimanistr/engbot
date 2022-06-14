# -*- coding: utf-8 -*-

# ---Dmitrij edit---
# Python 3.7.3

import asyncio
import aiohttp
from configparser import ConfigParser

from aionuts import Bot, Dispatcher, executor, types

from config import *
import lang


config = ConfigParser()
config.read('conf.cfg')
ID = config['DEFAULT']['id']
token = config['DEFAULT']['token']
dictionary = lang.Dictionary() # Empty

bot = Bot(token, id=ID, is_group=True)
dp = Dispatcher(bot)
prefixes = ['krem', 'крем']

@dp.message_handler(commands='help', prefixes=prefixes, ignore_case=True)
async def help(message):
    await message.answer(Messages.HELP)

@dp.message_handler(commands='d', prefixes=prefixes, ignore_case=True)
async def define(message):
    ''' Define type of message for correct response '''
    if message.is_command(): text = message.get_args()
    else: text = message.text

    commands = ('d', '/d@KremKremlebot', None)
    # Если это команда d ИЛИ команды нет вообще то ОК
    if message.get_command() not in commands:
        text = 'Unknown command'
        await message.reply(text)
        return True

    if text == '':
        text = 'Nothing to define'
        await message.answer(text)
        return True

    '''Do actual work, getting response'''
    d = 'collins'
    text = text.split()
    if len(text) > 1:
        if text[-1] in dictionary.dictionaries.keys():
            d = text[-1]
            text = text[:-1]

    word = ' '.join(text)
    definition = await dictionary.define(word, d)
    await message.answer(definition)

@dp.message_handler(commands='ds', prefixes=prefixes, ignore_case=True)
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

@dp.message_handler(commands='s', prefixes=prefixes, ignore_case=True)
async def send_synonyms(message):
    text = message.get_args()
    if text == '': response = 'Where is the word?'
    else: response = await dictionary.get_synonyms(text)
    await message.answer(response)

@dp.message_handler(commands='t', prefixes=prefixes, ignore_case=True)
async def translate(message):
    text = message.get_args()
    if text == '': response = 'А что переводить?'
    else: response = await dictionary.translate(text, 'en')
    await message.answer(response)

@dp.message_handler(commands='td', prefixes=prefixes, ignore_case=True)
async def translated(message):
    text = message.get_args()
    if text == '': response = 'А что переводить?'
    else: response = await dictionary.translate(text, 'de')
    await message.answer(response)

dp.register_message_handler(define, chat_type='private')


async def main():
    await dictionary.write() # Fill it
    await dp.start_polling()
    await dictionary.destroy()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Killed')
