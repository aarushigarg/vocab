from flask import Flask, make_response, render_template, request, redirect
app = Flask(__name__)
app.secret_key = b'd\x81\xc3i4b\xca\xc9D\xd9\x05\x12V\xa0\x031'

#from wordnet import get_rand_word, synset_sorter, word_exists

from oxford import get_rand_word, look_up_word

from db import account_finder_or_creater, get_user_by_id

from google.oauth2 import id_token
from google.auth.transport import requests

import os

from flask_login import LoginManager, current_user, login_user, logout_user
login_manager = LoginManager()
login_manager.init_app(app)

#loads the user object using the user id in session data
@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

#populates the user variable in the templates
@app.context_processor
def inject_user():
    return dict(user=current_user)

#routes to the home page and opens a random word
@app.route("/")
def home():
    rand_word = get_rand_word()
    return redirect(f"/word/{rand_word}")

#routes to the page of a word
@app.route("/word/<the_word>")
def word(the_word):
    word_meaning = look_up_word(the_word)
    display_word = the_word.replace("_", " ")
    return render_template("word_display.html", word=display_word, word_meaning=word_meaning)

#routes to a word that is searched
@app.route("/search")
def search():
    word = request.args.get("word", "")
    word = word.lower()
    #need to add if a word doesn't exist
    if word == "" :
        return redirect("/")
    return redirect(f"/word/{word}")

#logs in the user with google 
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

#logs out the user
@app.route("/logout")
def logout():
    resp = make_response(redirect("/"))
    logout_user()
    return resp