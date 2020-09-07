from flask import Flask, make_response, render_template, request, redirect
app = Flask(__name__)
app.secret_key = b'd\x81\xc3i4b\xca\xc9D\xd9\x05\x12V\xa0\x031'

from wordnet import get_rand_word, synset_sorter, word_exists

from db import account_finder_or_creater, get_user_by_id

from google.oauth2 import id_token
from google.auth.transport import requests

import os

from flask_login import LoginManager, current_user, login_user, logout_user
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

@app.context_processor
def inject_user():
    return dict(user=current_user)

@app.route("/")
def home():
    rand_word = get_rand_word()
    return redirect(f"/word/{rand_word}")

@app.route("/word/<the_word>")
def word(the_word):
    synsets = synset_sorter(the_word)
    display_word = the_word.replace("_", " ")
    synsets = synset_sorter(the_word)
    return render_template("word_display.html", word=display_word, synsets=synsets)

@app.route("/search")
def search():
    word = request.args.get("word", "")
    word = word.lower()
    if word == "" or not word_exists(word) :
        return redirect("/")
    return redirect(f"/word/{word}")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        token = request.form.get("token", "")
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), os.getenv("GOOGLE_CLIENT_ID"))
        user = account_finder_or_creater(idinfo["email"], idinfo["picture"])
        resp = make_response(redirect("/"))
        login_user(user, remember=True)
        return resp

@app.route("/logout")
def logout():
    resp = make_response(redirect("/"))
    logout_user()
    return resp