import psycopg2
import psycopg2.extras
import os
import json
import models

def connectToDb():
    conn = psycopg2.connect("host=rough-leaf-4031-db.flycast port=5432 dbname=vocabdb user=vocabuser password=vocabpass")
    conn.set_session(autocommit=True)
    return conn

def get_word(word):
    conn = connectToDb()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select * from cached_words where word = %s", [word])
    record = cur.fetchone()
    if not record:
        return None
    word_data = record["data"]
    return word_data

def get_saved_words_list_id_by_user_id(user_id):
    conn = connectToDb()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select * from word_defn_lists where user_id = %s and name = 'My saved words'", [user_id])
    d = cur.fetchone()
    return d[0]

def get_word_defn_id_by_word(word):
    conn = connectToDb()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select * from word_defns where word=%s", [word])
    d = cur.fetchone()
    return d[0]

def save_word(word, word_data):
    conn = connectToDb()
    word_data = json.dumps(word_data) #convert from dict to str for saving
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("insert into cached_words (word, data) values (%s, %s)", [word, word_data])
    

def save_word_for_user(user_id, word):
    conn = connectToDb()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select * from saved_words where user_id = %s and word = %s", [user_id, word])
    if not cur.fetchone():
        cur.execute("insert into saved_words (user_id, word) values (%s, %s)", [user_id, word])

def unsave_word_for_user(user_id, word):
    conn = connectToDb()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select * from saved_words where user_id = %s and word = %s", [user_id, word])
    if cur.fetchone():
        cur.execute("delete from saved_words where user_id = %s and word = %s", [user_id, word])

def get_saved_words(user_id):
    conn = connectToDb()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select word from saved_words where user_id = %s", [user_id])
    users_saved_words = cur.fetchall()
    for i in range(len(users_saved_words)):
        users_saved_words[i] = users_saved_words[i][0]
    return users_saved_words

def is_word_saved_by_user(user_id, word):
    conn = connectToDb()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select word from saved_words where user_id = %s and word = %s", [user_id, word])
    if cur.fetchone():
        return True
    else:
        return False