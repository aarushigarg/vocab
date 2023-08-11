import random

import psycopg2
import psycopg2.extras
import os

def connectToDb():
    conn = psycopg2.connect("host=rough-leaf-4031-db.flycast port=5432 dbname=vocabdb user=vocabuser password=vocabpass")
    conn.set_session(autocommit=True)
    return conn

connectToDb()

class User:
    def __init__(self, is_active, id, username, email, avatar):
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_active = is_active
        self.id = id
        self.username = username
        self.email = email
        self.avatar = avatar

    def get_id(self):
        return self.id

def account_finder_or_creater(email, avatar):
    conn = connectToDb()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select * from users where email = %s", [email])
    user = cur.fetchone()
    if not user:
        cur.execute("insert into users (username, email, avatar) values (%s, %s, %s) returning *", [email, email, avatar])
        user = cur.fetchone()
        cur.execute("insert into word_defn_lists (user_id, name) values (%s, %s)", [user["id"], "My saved words"])
    user_object = User(user["is_active"], user["id"], user["username"], user["email"], user["avatar"])
    return user_object

def get_user_by_id(id):
    conn = connectToDb()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select * from users where id = %s", [id])
    user = cur.fetchone()
    user_object = User(user["is_active"], user["id"], user["username"], user["email"], user["avatar"])
    return user_object



class WordDefnList():
    def __init__(self, id, user_id, name, create_time, update_time):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.create_time = create_time
        self.update_time = update_time
    
    @staticmethod
    def get_by_id(id):
        conn = connectToDb()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("select * from word_defn_lists where id=%s", [id])
        d = cur.fetchone()
        if not d:
            return None
        return WordDefnList(d["id"], d["user_id"], d["name"], d["create_time"], d["update_time"])

    @staticmethod
    def get_by_user_id(user_id):
        conn = connectToDb()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("select * from word_defn_lists where user_id=%s", [user_id])
        word_defn_lists = []
        d = cur.fetchone()
        while d:
            wdl = WordDefnList(d['id'], d['user_id'], d['name'], d["create_time"], d["update_time"])
            word_defn_lists.append(wdl)
            d = cur.fetchone()
        return word_defn_lists

    @staticmethod
    def get_user_by_wdl_id(id):
        conn = connectToDb()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("select user_id from word_defn_lists where id=%s", [id])
        return cur.fetchone()


    @staticmethod
    def create(user_id, name):
        conn = connectToDb()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("insert into word_defn_lists (user_id, name) values (%s, %s) returning *", [user_id, name])
        d = cur.fetchone()
        return WordDefnList(d['id'], d['user_id'], d['name'], d["create_time"], d["update_time"])

    def update_name(self, new_name):
        conn = connectToDb()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("update word_defn_lists set name=%s where id=%s", [new_name, self.id])
        self.name = new_name

    def delete(self):
        conn = connectToDb()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("delete from word_defn_lists where id=%s", [self.id])


class WordDefn():
    def __init__(self, id, word, part_of_speech, defn, examples, user_id, create_time, update_time):
        self.id = id
        self.word = word
        self.part_of_speech = part_of_speech
        self.defn = defn
        self.examples = examples
        self.user_id = user_id
        self.create_time = create_time
        self.update_time = update_time
    
    @staticmethod
    def create(word, pos, defn, examples, user_id):
        conn = connectToDb()
        examples = str(examples)
        examples = examples.replace('[', '{').replace(']', '}').replace('\'', '\"')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        print(pos)
        cur.execute("insert into word_defns (word, part_of_speech, defn, examples, user_id) values (%s, %s, %s, %s, %s) returning *", [word, pos, defn, examples, user_id])
        d = cur.fetchone()
        return WordDefn(d["id"], d["word"], d["part_of_speech"], d["defn"], d["examples"], d["user_id"], d["create_time"], d["update_time"])

    @staticmethod
    def get_by_id(id):
        conn = connectToDb()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("select * from word_defns where id=%s", [id])
        d = cur.fetchone()
        if not d:
            return None
        return WordDefn(d['id'], d["word"], d["part_of_speech"], d["defn"], d["examples"], d["user_id"], d["create_time"], d["update_time"])

    @staticmethod
    def update(word, part_of_speech, defn, examples, word_defn_id):
        conn = connectToDb()
        examples = str(examples)
        examples = examples.replace('[', '{').replace(']', '}').replace('\'', '\"')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("update word_defns set word=%s, part_of_speech=%s, defn=%s, examples=%s where id=%s returning *", [word, part_of_speech, defn, examples, word_defn_id])
        d = cur.fetchone()
        return WordDefn(d["id"], d["word"], d["part_of_speech"], d["defn"], d["examples"], d["user_id"], d["create_time"], d["update_time"])


def map_word_defn_to_list(word_defn_id, word_defn_list_id):
    conn = connectToDb()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("insert into word_defn_list_map (word_defn_id, word_defn_list_id) values (%s, %s)", [word_defn_id, word_defn_list_id])

def get_word_defns_from_list(word_defn_list_id):
    conn = connectToDb()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select word_defn_id from word_defn_list_map where word_defn_list_id=%s", [word_defn_list_id])
    return cur.fetchall()

def delete_map_of_word_defn_to_list(word_defn_id, word_defn_list_id):
    conn = connectToDb()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("delete from word_defn_list_map where word_defn_id=%s and word_defn_list_id=%s", [word_defn_id, word_defn_list_id])

def delete_word_defn(word_defn_id):
    conn = connectToDb()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("delete from word_defns where id=%s", [word_defn_id])

class PracticeSession():
    def __init__(self, id, user_id, wdl_id, word_defn_ids, current_index, create_time, update_time):
        self.id = id
        self.user_id = user_id
        self.wdl_id = wdl_id
        self.word_defn_ids = word_defn_ids
        self.create_time = create_time
        self.update_time = update_time

    @staticmethod
    def create(user_id, wdl_id, word_defn_ids):
        conn = connectToDb()
        random.shuffle(word_defn_ids)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("insert into practice_sessions (user_id, wdl_id, word_defn_ids) values (%s, %s, %s) returning *", [user_id, wdl_id, word_defn_ids])
        d = cur.fetchone()
        return PracticeSession(d["id"], d["user_id"], d["wdl_id"], d["word_defn_ids"], d["current_index"], d["create_time"], d["update_time"])

    @staticmethod
    def get_by_id(session_id):
        conn = connectToDb()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("select * from practice_sessions where id=%s", [session_id])
        return cur.fetchone()


class Feedback():
    def __init__(self, id, user_id, word_defn_id, difficulty_level, create_time, update_time):
        self.id = id
        self.user_id = user_id
        self.word_defn_id = word_defn_id
        self.difficulty_level = difficulty_level
        self.create_time = create_time
        self.update_time = update_time