import psycopg2
import psycopg2.extras
import os

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
conn.set_session(autocommit=True)

def account_finder_or_creater(email, avatar):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select * from users where email = %s", [email])
    user = cur.fetchone()
    if not user:
        cur.execute("insert into users (username, email, avatar) values (%s, %s, %s)", [email, email, avatar])
        cur.execute("select * from users where email = %s", [email])
        user = cur.fetchone()
    return user

def get_user_by_id(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select * from users where id = %s", [id])
    return cur.fetchone()