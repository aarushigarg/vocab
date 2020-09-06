import psycopg2
import psycopg2.extras
import os

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
conn.set_session(autocommit=True)

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
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select * from users where email = %s", [email])
    user = cur.fetchone()
    if not user:
        cur.execute("insert into users (username, email, avatar) values (%s, %s, %s)", [email, email, avatar])
        cur.execute("select * from users where email = %s", [email])
        user = cur.fetchone()
    user_object = User(user["is_active"], user["id"], user["username"], user["email"], user["avatar"])
    return user_object

def get_user_by_id(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select * from users where id = %s", [id])
    user = cur.fetchone()
    user_object = User(user["is_active"], user["id"], user["username"], user["email"], user["avatar"])
    return user_object