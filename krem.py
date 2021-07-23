# -*- coding: utf-8 -*-

import os
import json
import asyncio
from queue import LifoQueue

import requests

import vk
import lang

token = os.getenv('TOKEN')
name = 0
stack = LifoQueue()

class Bot:
    def pin_audio_attachment(self, text, vkapi, peer_id):
        # For answers check the https://vk.com/dev/upload_files_3 (12's checkpoint)
        f = open('sounds/%s.ogg'%(text), 'rb')
        data = {'file':f}

        link = vkapi.get('docs.getMessagesUploadServer', peer_id=peer_id, type='audio_message')
        link = link['response']['upload_url']
        load_file = requests.post(link, files = data).json()
        fileid = load_file['file']

        fileid = vkapi.get('docs.save', file=fileid, title=text+'.ogg')
        f.close()
        attachment = 'doc%s_%s_%s'%(fileid['response']['audio_message']['owner_id'],
                                    fileid['response']['audio_message']['id'],
                                    fileid['response']['audio_message']['access_key'])
        return attachment

class Krem():
    def __init__(self, peer_id, random_id):
        # self.text = text[
        self.peer_id = peer_id
        self.random_id = random_id

    async def give_help(self):
        """ SEND ALL THE COMMANDS WHICH BOT CAN GET """
        message = '''Крем, Functions:\n
    / Get help
    krem help\n
    / Get the meaning of a word
    krem м/m/meaning <eng word>
    / Get the full meaning with pronunciation (other definitions)
    krem фм/fm <eng word>\n
    / Get all the existing synonyms of word
    krem с/s/синонимы/synonyms <eng word>
    / Get the translate of a sentence/word
    krem т/t/translate <eng/rus sentence>
    / Get the pronunciation or the text
    krem say <eng word/sentence>\n
    // Get the chinese to russian translate and back
    krem рис/fig <chinese/rus word/sentence>'''
        return message

    async def give_info(self):
        pass

    async def give_meaning(self, word):
        language = lang.language(word)
        message = language.define()
        return message

    async def give_full_meaning(self, text, vkapi):
        """ Send all the definitions of word to the user + prononciaton """
        language = lang.language(text)
        response = language.fdefine()
        sound = language.pron()
        message = response

        with open('sounds/%s.ogg'%(text), 'wb') as f:
            f.write(sound)

        attachment = Bot.pin_audio_attachment(self, text, vkapi, self.peer_id)
        vkapi.get('messages.send', peer_id=self.peer_id, random_id=self.random_id, message=message, attachment=attachment)

    async def give_translate(self, text):
        language = lang.language(text)
        message = language.translate()
        return message

    async def fig(self, text):
        """ Translate russian to chinese and back """
        language = lang.language(text)
        message = language.kfig()
        return message

    async def say(self, text, vkapi):
        """ Combine different audio files into one audio message """
        global name
        for i in range(len(text)):
            language = lang.language(text[i])
            if i == 0:
                say = language.pron()
            else:
                say+=language.pron()

        with open('sounds/say/%s.ogg'%(name), 'wb') as f:
            f.write(say)

        attachment = Bot.pin_audio_attachment(self, text, vkapi, self.peer_id)
        name+=1
        vkapi.get('messages.send', peer_id=self.peer_id, random_id=self.random_id, attachment=attachment)


async def logic(vkapi):
    updates = stack.get()
    print(updates)

    if updates['type'] == 'message_new':
        text = updates['object']['message']['text']
        text = text.lower().split(' ', 2)
        if len(text) > 1 and text[0] in ("krem", "крем"):
            peer_id = updates['object']['message']['peer_id']
            random_id = updates['object']['message']['random_id']
            krem = Krem(peer_id, random_id)

            if text[1] == 'help':
                task = asyncio.create_task(krem.give_help())
                message = await task
                vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message=message)

            if text[1] in ('fig', 'рис'):
                try:
                    text = text[2]
                    task = asyncio.create_task(krem.fig(text))
                    message = await task
                    vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message=message)
                except:
                    message = "Something wrong, use only russian and chinese languages"
                    vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message=message)
            if text[1] in ('t', 'т', 'translate'):
                try:
                    text = text[2]
                    task = asyncio.create_task(krem.give_translate(text))
                    message = await task
                    vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message=message)
                except:
                    message = 'Something worng, use only russian and englins languages'
                    vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message=message)
            if text[1] in ('fm', 'фм'):
                try:
                    text = text[2]
                    task = asyncio.create_task(krem.give_full_meaning(text, vkapi))
                    await task
                except:
                    vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message="Try another word")
            if text[1] == 'say':
                try:
                    text = text[2]
                    task = asyncio.create_task(krem.say(text, vkapi))
                    await task
                except:
                    vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message="Try another word")
            if text[1] in ('m', 'м', 'meaning'):
                try:
                    word = text[2]
                    task = asyncio.create_task(krem.give_meaning(word))
                    message = await task
                    vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message=message)
                except:
                    vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message="Try another word")

            if text[1] in ('s', 'с', 'синонимы', 'synonyms'):
                try:
                    word = text[2]
                    m = lang.language(word)
                    message = m.give_synonyms()
                    vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message=message)
                except:
                    vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message="Try another word")

            # Clear cache after script
            # from streamlit import caching
            # caching.clear_cache()

async def get_updates(vkapi):
    data = vkapi.ListenLP()
    if data != []:
        for i in data:
            stack.put(i)

async def main():
    vkapi = vk.vkapi(token)
    vkapi.GetLP()

    while True:
        task1 = asyncio.create_task(get_updates(vkapi))
        task2 = asyncio.create_task(logic(vkapi))
        await asyncio.gather(task1, task2)

if __name__ == '__main__':
    asyncio.run(main())
