# -*- coding: utf-8 -*-

# ---Dmitrij edit---
# Python 3.10.5

import asyncio
import logging
from aionuts import Bot, Dispatcher
from dataclasses import dataclass

from middlewares import ContentMiddleware
from lang import Dictionary
from config import *

logging.basicConfig(level=logging.INFO)
bot = Bot(token=VK_TOKEN, id=VK_GROUP_ID, is_group=True)
dp = Dispatcher(bot)
dp.middleware.setup(ContentMiddleware())
lang = Dictionary()


@dataclass
class UserRequest:
    """Represents user's message in more useful way"""
    word: str
    dictionary: str = 'collins'

def format_user_input(word):
    """Checks if the last word in the text is the name of a dictionary
    returns UserRequest object that contains the word and the dictionary"""
    text = word.rsplit(' ', 1)
    if text[-1] in lang.dictionaries and len(text) > 1:
        return UserRequest(text[0], text[-1])
    return UserRequest(word)


@dp.message_handler(commands='help', prefixes=PREFIXES, ignore_case=True)
async def help(message):
    await message.answer(HELP_MESSAGE)

@dp.message_handler(commands='d', prefixes=PREFIXES, ignore_case=True)
async def define(message):
    text = message.text
    if message.is_command():
        text = message.get_args()

    # check if msg is a command 'd' or not a command at all
    commands = ('d', '/d', '/d@KremKremlebot', None)
    if message.get_command() not in commands:
        text = 'Unknown command'
        await message.reply(text)
        return True

    text = format_user_input(text)
    dictionary = getattr(lang, text.dictionary)
    definition = await dictionary.define(text.word)
    await message.answer(definition)

@dp.message_handler(commands='ds', prefixes=PREFIXES, ignore_case=True)
async def defines(message):
    text = message.get_args()
    text = format_user_input(text)
    dictionary = getattr(lang, text.dictionary)
    definition = await dictionary.defines(text.word)
    await message.answer(definition)

@dp.message_handler(commands='s', prefixes=PREFIXES, ignore_case=True)
async def send_synonyms(message):
    text = message.get_args()
    response = await lang.get_synonyms(text)
    await message.answer(response)

@dp.message_handler(commands='t', prefixes=PREFIXES, ignore_case=True)
async def translate(message):
    text = message.get_args()
    response = await lang.translate(text, 'en')
    await message.answer(response)

dp.register_message_handler(define, chat_type='private')

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot has stopped')
