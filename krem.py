# -*- coding: utf-8 -*-

import os
import json
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

    def give_help(self):
        """ SEND ALL THE COMMANDS WHICH BOT CAN GET """
        message = '''Крем, Functions:\n
    / Get help
    krem help\n
    / Get the meaning of a word
    krem m <eng word>
    krem meaning <eng word>\n
    / Get the full meaning with pronunciation (other definitions)
    krem fm <eng word>\n
    / Get the translate of a sentence/word
    krem t <eng/rus sentence>
    krem т <eng/rus sentence>
    krem translate <eng/rus sentence>\n
    / Get the pronunciation or the text
    krem say <eng word/sentence>\n
    // Get the chinese to russian translate and back
    krem fig <chinese/rus word/sentence>
    krem рис <chinese/rus word/senten'''
        return message

    def give_info(self):
        pass

    def give_meaning(self, word):
        language = lang.language(word)
        message = language.define()
        return message

    def give_full_meaning(self, text, vkapi):
        """ Send all the definitions of word to the user + prononciaton """
        language = lang.language(text)
        response = language.fdefine()
        sound = language.pron()
        message = response

        with open('sounds/%s.ogg'%(text), 'wb') as f:
            f.write(sound)

        attachment = Bot.pin_audio_attachment(self, text, vkapi, self.peer_id)
        vkapi.get('messages.send', peer_id=self.peer_id, random_id=self.random_id, message=message, attachment=attachment)

    def give_translate(self, text):
        language = lang.language(text)
        message = language.translate()
        return message

    def fig(self, text):
        """ Translate russian to chinese and back """
        language = lang.language(text)
        message = language.kfig()
        return message

    def say(self, text, vkapi):
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

if __name__ == '__main__':
    vkapi = vk.vkapi(token)
    vkapi.GetLP()

    while True:
        updates = vkapi.ListenLP()
        print(updates)

        if updates['type'] == 'message_new':
            text = updates['object']['message']['text']
            text = text.split(' ', 2)
            if len(text) > 1 and text[0] == 'krem' or text[0] == "Krem" or text[0] == "Крем" or text[0] == "крем":
                peer_id = updates['object']['message']['peer_id']
                random_id = updates['object']['message']['random_id']
                krem = Krem(peer_id, random_id)

                if text[1] == 'help':
                    message = krem.give_help()
                    vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message=message)

                if text[1] == 'fig' or text[1] == 'рис':
                    try:
                        text = text[2]
                        message = krem.fig(text)
                        vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message=message)
                    except:
                        message = "Something wrong, use only russian and chinese languages"
                        vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message=message)
                if text[1] == 't' or text[1] == 'т' or text[1] == 'translate':
                    try:
                        text = text[2]
                        message = krem.give_translate(text)
                        vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message=message)
                    except:
                        message = 'Something worng, use only russian and englins languages'
                        vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message=message)
                if text[1] == 'fm':
                    try:
                        text = text[2]
                        krem.give_full_meaning(text, vkapi)
                    except:
                        vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message="Try another word")
                if text[1] == 'say':
                    try:
                        text = text[2]
                        # text = text[2].split()
                        krem.say(text, vkapi)
                    except:
                        vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message="Try another word")
                if text[1] == 'm' or text[1] == 'meaning':
                    try:
                        word = text[2]
                        # stack.put([peer_id, random_id, word])
                        message = krem.give_meaning(word)
                        vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message=message)
                    except:
                        vkapi.get('messages.send', peer_id=peer_id, random_id=random_id, message="Try another word")

                # Clear cache after script
                from streamlit import caching
                caching.clear_cache()
