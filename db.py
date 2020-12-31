import psycopg2
import psycopg2.extras
import os
import json

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
conn.set_session(autocommit=True)

def get_word(word):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select * from cached_words where word = %s", [word])
    record = cur.fetchone()
    if not record:
        return None
    word_data = record["data"]
    return word_data

def save_word(word, word_data):
    word_data = json.dumps(word_data) #convert from dict to str for saving
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("insert into cached_words (word, data) values (%s, %s)", [word, word_data])

def save_word_for_user(user_id, word):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select * from saved_words where user_id = %s and word = %s", [user_id, word])
    if not cur.fetchone():
        cur.execute("insert into saved_words (user_id, word) values (%s, %s)", [user_id, word])

def unsave_word_for_user(user_id, word):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("delete from saved_words where user_id = %s and word = %s", [user_id, word])

def get_saved_words(user_id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select word from saved_words where user_id = %s", [user_id])
    users_saved_words = cur.fetchall()
    users_saved_words = users_saved_words
    return users_saved_words

def word_saved_by_user_or_not(user_id, word):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select word from saved_words where user_id = %s and word = %s", [user_id, word])
    if cur.fetchone():
        return True
    else:
        return False