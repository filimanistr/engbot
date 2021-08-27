# -*- coding: utf-8 -*-

# ---Wells edit---
# Python 3.9.6

import asyncio
from threading import Thread
from queue import LifoQueue
from configparser import ConfigParser

import requests

from vkapi import vk
import lang

config = ConfigParser()
config.read('conf.cfg')
token = config['DEFAULT']['token']
stack = LifoQueue()

class Krem():
    def __init__(self, vkbot, peer_id, random_id):
        self.vkbot = vkbot
        self.peer_id = peer_id
        self.random_id = random_id

    async def give_help(self):
        """ SEND ALL THE COMMANDS WHICH BOT CAN GET """
        message = '''Крем, Functions:\n
/ Get help
krem help\n
/ Get the meaning of a word
krem м/m/meaning <eng word>
/ Get the full meaning (other definitions)
krem фм/fm <eng word>\n
/ Get all the existing synonyms of word
krem с/s/синонимы/synonyms <eng word>
/ Get the translate of a sentence/word
krem т/t/translate <eng/rus sentence>
// Get the chinese to russian translate and back
krem рис/fig <chinese/rus word/sentence>'''
        self.vkbot.messages.send(peer_id=self.peer_id, random_id=self.random_id, message=message)

    async def give_meaning(self, word, dictionary='collins'):
        language = lang.language(word)
        message = await language.define(dictionary)
        self.vkbot.messages.send(peer_id=self.peer_id, random_id=self.random_id, message=message)

    async def give_full_meaning(self, text, dictionary='collins'):
        """ Send all the definitions of word to the user + prononciaton """
        language = lang.language(text)
        response = await language.fdefine(dictionary)
        message = response
        self.vkbot.messages.send(peer_id=self.peer_id, random_id=self.random_id, message=message)

    async def give_synonyms(self, text):
        language = lang.language(text)
        message = await language.give_synonyms()
        self.vkbot.messages.send(peer_id=self.peer_id, random_id=self.random_id, message=message)

    async def give_translate(self, text):
        language = lang.language(text)
        message = await language.translate()
        self.vkbot.messages.send(peer_id=self.peer_id, random_id=self.random_id, message=message)

    async def fig(self, text):
        """ Translate russian to chinese and back """
        language = lang.language(text)
        message = await language.kfig()
        self.vkbot.messages.send(peer_id=self.peer_id, random_id=self.random_id, message=message)


async def handler(vkbot):
    updates = stack.get()
    print(updates)

    if updates['type'] == 'message_new':
        text = updates['object']['message']['text']
        text = text.lower().split()
        if len(text) > 1 and text[0] in ("krem", "крем"):
            peer_id = updates['object']['message']['peer_id']
            random_id = updates['object']['message']['random_id']
            krem = Krem(vkbot, peer_id, random_id)

            if text[1] == 'help':
                asyncio.create_task(krem.give_help())

            if len(text) > 2:
                word = '-'.join([str(elem) for elem in text[2:]])

                if text[1] in ('fig', 'рис'):
                    asyncio.create_task(krem.fig(word))
                if text[1] in ('t', 'т', 'translate'):
                    asyncio.create_task(krem.give_translate(word))
                if text[1] in ('fm', 'фм'):
                    asyncio.create_task(krem.give_full_meaning(word))

                if text[1] in ('m', 'м', 'meaning'):
                    asyncio.create_task(krem.give_meaning(word))
                if text[1] in ('s', 'с', 'синонимы', 'synonyms'):
                    asyncio.create_task(krem.give_synonyms(word))

                if text[1] in ("collins", "urban", "cambridge") and text[2] in ("m", "м", "meaning", "fm", "фм"):
                    command = text[2]
                    word = text[3]
                    dictionary = text[1]

                    if command in ("fm", "фм"):
                        asyncio.create_task(krem.give_full_meaning(word, dictionary))
                    if command in ("m", "м", "meaning"):
                        asyncio.create_task(krem.give_meaning(word, dictionary))


def longpoll(event):
    stack.put(event)

def main(vkbot):
    while True:
        try:
            asyncio.run(handler(vkbot))
        except:
            print("Something went wrong")

        # Clear cache after script
        from streamlit import caching
        caching.clear_cache()


if __name__ == "__main__":
    vkbot = vk.vk(token, id=206096513, is_group=True)

    thread = Thread(target=main, args=(vkbot,))
    thread.start()

    vkbot.lp_loop(longpoll)
