from configparser import ConfigParser
config = ConfigParser()
config.read('conf.cfg')

VK_GROUP_ID = config['VK']['ID']
VK_TOKEN  = config['VK']['TOKEN']
TG_TOKEN = config['TG']['TOKEN']

COLLINS_DICTIONARY_URL = 'https://www.collinsdictionary.com/dictionary/english'
URBAN_DICTIONARY_URL = 'https://api.urbandictionary.com/v0/'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none', 'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}


PREFIXES = ['krem', 'крем']
HELP_MESSAGE = '''Получить определениe слова
krem d eng_word
Получить определения слов
krem ds eng_word
Перевод с англа на русский
krem t ru/eng_text
Получить все синонимы слова
krem s eng_word

Поддерживаются 2 словаря:
collins (default) и urban, юзается так:
krem d eng_word dict_name
krem ds eng_word dict_name
'''

ERROR_EMPTY_MESSAGE = '''
I've got nothing to work with
send me some text
'''

DEFINITION_MESSAGE_PATTERN = '{word} ({grammar_phorm}) - {definition}\n'
DEFINITIONS_MESSAGE_PATTERN = '{num}. {grammar_phorm}\n{definition}\n'
URBAN_DEFINITION_MESSAGE_PATTERN = '{word} - {definition}\nExample: {example}'
URBAN_DEFINITIONS_MESSAGE_PATTERN = 'Definition: {definition}\n\nExample: {example}\n\n'

