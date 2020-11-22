import random
import requests

import db 

import oxforddata

import os

def get_rand_word():
    words = ["hello", "you", "book", "there", "run"]
    return random.choice(words)

def get_word_from_oxford(word):
    language = "en-us"
    word_id = word
    url =  "https://od-api.oxforddictionaries.com:443/api/v2/entries/" + language + "/" + word_id.lower()
    r = requests.get(url, headers={"app_id": os.getenv("OXFORD_APP_ID"), "app_key": os.getenv("OXFORD_APP_KEY")})
    if r.status_code != 200:
        print("Oxfrod API call failed")
        print(r.status_code)
        print(r.text)
    data = r.json()
    return data

def look_up_word(word):
    word = word.lower()
    word_data = db.get_word(word)
    if word_data == None:
        word_data = get_word_from_oxford(word)
        db.save_word(word, word_data)
    word_meaning = oxforddata.word_meaning_builder(word, word_data)
    return word_meaning