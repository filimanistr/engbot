# -*- coding: utf-8 -*-

import os
import json

import requests

import vk
import lang

token = os.getenv('TOKEN')
name = 0


class Krem(vk.vkapi):
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
        requests.get('https://api.vk.com/method/messages.send?peer_id=%s&random_id=%s&message=%s&access_token=%s&v=5.131'%(self.peer_id, self.random_id, message, token))

    def give_meaning(self, word):
        language = lang.language(word)
        message = language.define()

        requests.get('https://api.vk.com/method/messages.send?peer_id=%s&random_id=%s&message=%s&access_token=%s&v=5.131'%(self.peer_id, self.random_id, message, token))

    def give_full_meaning(self, text):
        pass

    def give_translate(self, text):
        language = lang.language(text)
        message = language.translate()
        
        requests.get('https://api.vk.com/method/messages.send?peer_id=%s&random_id=%s&message=%s&access_token=%s&v=5.131'%(self.peer_id, self.random_id, message, token))

def kfullmeaning(peer_id, random_id, text):
    """ SEND ALL THE DEFINITIONS OF WORD TO THE USER + prononciaton """
    text = text[2]
    language = lang.language(text)
    response = language.fdefine()
    sound = language.pron()
    message = response

    with open('sounds/%s.ogg'%(text), 'wb') as f:
        f.write(sound)

    # For answers check the https://vk.com/dev/upload_files_3 (12's checkpoint)
    f = open('sounds/%s.ogg'%(text), 'rb')
    data = {'file':f}
    rlink = requests.get('https://api.vk.com/method/docs.getMessagesUploadServer?peer_id=%s&type=audio_message&access_token=%s&v=5.131'%(peer_id, token)).text
    mlink = json.loads(rlink)
    mlink = mlink['response']['upload_url']

    rrlink = requests.post(mlink, files = data).json()
    file_ = rrlink['file']

    rrlink = requests.get('https://api.vk.com/method/docs.save?file=%s&title=%s.ogg&access_token=%s&v=5.131'%(file_, text, token)).text
    mmlink = json.loads(rrlink)
    response = requests.get('https://api.vk.com/method/messages.send?peer_id=%s&random_id=%s&message=%s&attachment=doc%s_%s_%s&access_token=%s&v=5.131'%(peer_id, random_id, message, mmlink['response']['audio_message']['owner_id'], mmlink['response']['audio_message']['id'], mmlink['response']['audio_message']['access_key'], token))
    f.close()

def ksay (peer_id, random_id, text):
    """ COMBINE DIFFERENT AUDIO FILES INTO ONE AUDIO MESSAGE """
    global name
    textt = text[2].split()
    for i in range(len(textt)):
        language = lang.language(textt[i])
        if i == 0:
            say = language.pron()
        else:
            say+=language.pron()

    with open('sounds/say/%s.ogg'%(name), 'wb') as f:
        f.write(say)

    # For answers check the https://vk.com/dev/upload_files_3 (12's checkpoint)
    f = open('sounds/say/%s.ogg'%(name), 'rb')
    data = {'file':f}
    rlink = requests.get('https://api.vk.com/method/docs.getMessagesUploadServer?peer_id=%s&type=audio_message&access_token=%s&v=5.131'%(peer_id, token)).text
    mlink = json.loads(rlink)
    mlink = mlink['response']['upload_url']

    rrlink = requests.post(mlink, files = data).json()
    file_ = rrlink['file']

    rrlink = requests.get('https://api.vk.com/method/docs.save?file=%s&title=%s.ogg&access_token=%s&v=5.131'%(file_, text, token)).text
    mmlink = json.loads(rrlink)
    requests.get('https://api.vk.com/method/messages.send?peer_id=%s&random_id=%s&attachment=doc%s_%s_%s&access_token=%s&v=5.131'%(peer_id, random_id, mmlink['response']['audio_message']['owner_id'], mmlink['response']['audio_message']['id'], mmlink['response']['audio_message']['access_key'], token))
    name+=1
    f.close()
def kfig(peer_id, random_id, text):
    """ TRABSLATE RUSSIAN TO CHINESE AND BACK """
    text = text[2]

    language = lang.language(text)
    response = language.kfig()

    message = response
    requests.get('https://api.vk.com/method/messages.send?peer_id=%s&random_id=%s&message=%s&access_token=%s&v=5.131'%(peer_id, random_id, message, token))


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
                    krem.give_help()

                if text[1] == 'fig' or text[1] == 'рис':
                    try:
                        kfig(peer_id, random_id, text)
                    except:
                        requests.get('https://api.vk.com/method/messages.send?peer_id=%s&random_id=%s&message=Something wrong, use only russian and chinese languages&access_token=%s&v=5.131'%(peer_id, random_id, token))

                if text[1] == 't' or text[1] == 'т' or text[1] == 'translate':
                    try:
                        text = text[2]
                        krem.give_translate(text)
                    except:
                        requests.get('https://api.vk.com/method/messages.send?peer_id=%s&random_id=%s&message=Something worng, use only russian and englins languages&access_token=%s&v=5.131'%(peer_id, random_id, token))

                if text[1] == 'fm':
                    try:
                        kfullmeaning(peer_id, random_id, text)
                    except:
                        requests.get('https://api.vk.com/method/messages.send?peer_id=%s&random_id=%s&message=Try another word&access_token=%s&v=5.131'%(peer_id, random_id, token))

                if text[1] == 'say':
                    try:
                        ksay(peer_id, random_id, text)
                    except:
                        requests.get('https://api.vk.com/method/messages.send?peer_id=%s&random_id=%s&message=Try another word&access_token=%s&v=5.131'%(peer_id, random_id, token))

                if text[1] == 'm' or text[1] == 'meaning':
                    try:
                        word = text[2]
                        krem.give_meaning(word)
                    except:
                        requests.get('https://api.vk.com/method/messages.send?peer_id=%s&random_id=%s&message=Try another word&access_token=%s&v=5.131'%(peer_id, random_id, token))
                
                # Clear cache after script
                # from streamlit import caching
                # caching.clear_cache()
