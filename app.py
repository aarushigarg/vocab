from flask import Flask, make_response, render_template, request, redirect
app = Flask(__name__)
app.secret_key = b'd\x81\xc3i4b\xca\xc9D\xd9\x05\x12V\xa0\x031'

from wordnet import get_rand_word, synset_sorter

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
    display_word = rand_word.replace("_", " ")
    synsets = synset_sorter(rand_word)
    return render_template("home.html", word=display_word, synsets=synsets)

@app.route("/search")
def search():
    word = request.args.get("word", "")
    word = word.lower()
    if word == "":
        return redirect("/")
    synsets = synset_sorter(word)
    display_word = word.replace("_", " ")
    return render_template("home.html", word=display_word, synsets=synsets)

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