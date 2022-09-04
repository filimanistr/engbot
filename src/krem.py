# -*- coding: utf-8 -*-

# ---Dmitrij edit---
# Python 3.10.5

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
connor = ['канар', 'каннар', 'конор', 'коннор', 'конар', 'коннар', 'connor']
split = [*prefixes, *connor]

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

    if message.get_prefix() not in prefixes:
        text = "unknown command"
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

import json
from ctypes import *
from PIL import Image
import numpy as np

cair = CDLL('./liball.so')
cair.main.restype = None
cair.main.argtypes = c_int,POINTER(c_char_p)

def to_bitmap(image):
    img = Image.open(image)
    img.save('img/in.bmp')

@dp.message_handler(commands=['кас', 'cas'], prefixes=split, ignore_case=True)
async def pie(message):
    global session
    url = message.event['object']['message']['attachments'][0]['photo']['sizes'][-1]['url']
    async with session.get(url) as ret:
        html = await ret.read()

    f = open('img/in.jpg', 'wb')
    f.write(html)
    f.close()

    to_bitmap('img/in.jpg')
    args =(c_char_p * 14)(b'-C', b'3', b'-T', b'1', b'-E', b'1', b'-I', b'img/in.bmp', b'-P', b'50', b'-R', b'0', b'-O', b'img/out.jpg' )
    cair.main(len(args),args)

    f = open('img/out.jpg', 'rb')
    url = await bot.photos.getMessagesUploadServer(peer_id=message.peer_id)
    async with session.post(url['response']['upload_url'], data={'photo':f}) as ret:
        html = await ret.read()

    f.close()
    html = json.loads(html)
    url = await bot.photos.saveMessagesPhoto(photo = html['photo'],
                                            server = html['server'],
                                            hash=html['hash'])
    attachment = "photo%s_%s"%(url['response'][0]['owner_id'],
                                url['response'][0]['id'])
    await message.answer(message="Ваша пикча: ", attachment=attachment)

dp.register_message_handler(define, chat_type='private')


async def main():
    global session
    s = lang.Scrapper()
    session = await s.get_session()

    await dictionary.write() # Fill it
    await dp.start_polling()
    await dictionary.destroy()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Killed')
