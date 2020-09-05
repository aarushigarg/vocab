from flask import Flask, make_response, render_template, request, redirect
app = Flask(__name__)

from wordnet import get_rand_word, synset_sorter

from db import account_finder_or_creater, get_user_by_id

from google.oauth2 import id_token
from google.auth.transport import requests

import os


@app.route("/")
def home():
    rand_word = get_rand_word()
    display_word = rand_word.replace("_", " ")
    synsets = synset_sorter(rand_word)
    if "user_id" in request.cookies:
        user = get_user_by_id(request.cookies.get("user_id"))
    else:
        user = None
    return render_template("home.html", word=display_word, synsets=synsets, user=user)

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
        resp.set_cookie("user_id", str(user["id"]))
        return resp

@app.route("/logout")
def logout():
    resp = make_response(redirect("/"))
    resp.delete_cookie("user_id")
    return resp