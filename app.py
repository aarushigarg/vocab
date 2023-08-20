from flask import Flask, make_response, render_template, request, redirect
app = Flask(__name__)
app.secret_key = b'd\x81\xc3i4b\xca\xc9D\xd9\x05\x12V\xa0\x031'

from oxford import get_rand_word, look_up_word

from db import save_word_for_user, unsave_word_for_user, get_saved_words, is_word_saved_by_user

from models import account_finder_or_creater, get_user_by_id, WordDefnList, WordDefn, map_word_defn_to_list, get_word_defns_from_list, delete_map_of_word_defn_to_list, delete_word_defn, PracticeSession, Feedback

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
    if current_user.is_authenticated:
        wdls = WordDefnList.get_by_user_id(current_user.id)
        return render_template("logged_in_home_page.html", wdls=wdls)
    else:
        return render_template("logged_out_home_page.html")


#routes to the page of a word
@app.route("/word/<the_word>")
def word(the_word):
    word_meaning = look_up_word(the_word)
    display_word = the_word.replace("_", " ")
    word_save_status = is_word_saved_by_user(current_user.id, display_word)
    return render_template("word_display.html", word=display_word, word_meaning=word_meaning, word_save_status=word_save_status)


#routes to a word that is searched
@app.route("/search")
def search():
    word = request.args.get("word", "")
    word = word.lower()
    #need to add if a word doesn't exist
    if word != "" :
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


#saves the word
@app.route("/save-word", methods=['POST'])
def save_word():
    word = request.form.get("word", "")
    command = request.form.get("command", "")
    user_id = current_user.id
    if command == "save":
        save_word_for_user(user_id, word)
    else:
        unsave_word_for_user(user_id, word)
    return ""

#shows a list of definitions
@app.route("/word-definition-list/<wdl_id>")
def word_defn_list(wdl_id):
    wdl = WordDefnList.get_by_id(wdl_id)
    word_defn_ids = get_word_defns_from_list(int(wdl_id))

    for i in range(len(word_defn_ids)):
        word_defn_ids[i] = word_defn_ids[i][0]

    word_defns = []
    for word_defn_id in word_defn_ids:
        word_defns.append(WordDefn.get_by_id(word_defn_id))

    if wdl.getName() == "My saved words":
        return render_template("my_saved_words.html", wdl=wdl, word_defns=word_defns)
    else:
        return render_template("word_defn_list.html", wdl=wdl, word_defns=word_defns)


#renames the list
@app.route("/word-definition-list/<wdl_id>/rename", methods=['GET', 'POST'])
def word_defn_list_rename(wdl_id):
    wdl = WordDefnList.get_by_id(wdl_id)

    if request.method == "GET":
        return render_template("wdl_rename.html", wdl=wdl)
    else:
        name = request.form.get("name", "")
        wdl.update_name(name)
        return redirect(f"/word-definition-list/{wdl.id}")


#deletes the list
@app.route("/word-definition-list/<wdl_id>/delete", methods=['GET', 'POST'])
def word_defn_list_delete(wdl_id):
    wdls = WordDefnList.get_by_user_id(current_user.id)
    if len(wdls) < 2:
        return redirect(f"/word-definition-list/{wdl_id}")
    
    wdl = WordDefnList.get_by_id(wdl_id)
    if request.method == "GET":
        return render_template("wdl_delete.html", wdl=wdl)
    else:
        wdl.delete()
        return redirect("/")


#creates a list
@app.route("/word-definition-list/create", methods=['GET', 'POST'])
def word_defn_list_create():
    if request.method == "GET":
        return render_template("wdl_create.html")
    else:
        name = request.form.get("name", "")
        wdl = WordDefnList.create(current_user.id, name)
        return redirect(f"/word-definition-list/{wdl.id}")

#TODO
#adds an existing word definition to a list
@app.route("/word-definition-list/<wdl_id>/add", methods=['GET', 'POST'])
def word_defn_list_add(wdl_id):
    pass

#adds a custom word definition to a list
@app.route("/word-definition-list/<wdl_id>/add-custom", methods=['GET', 'POST'])
def word_defn_list_add_custom(wdl_id):
    wdl = WordDefnList.get_by_id(wdl_id)
    if request.method == "GET":
        return render_template("wdl_add_custom.html", wdl=wdl)
    else:
        word = request.form.get("word", "")
        pos = request.form.get("pos", "")
        defn = request.form.get("defn", "")
        example1 = request.form.get("example1", "")
        example2 = request.form.get("example2", "")
        example3 = request.form.get("example3", "")
        examples = []

        if example1 != None:
            examples.append(example1)
        if example2 != None:
            examples.append(example2)
        if example3 != None:
            examples.append(example3)

        word_defn = WordDefn.create(word, pos, defn, examples, current_user.id)
        map_word_defn_to_list(word_defn.id, wdl_id)
        return render_template("wdl_add_custom.html", wdl=wdl)


@app.route("/word-definition/<wdl_id>/<word_defn_id>/edit", methods=['GET', 'POST'])
def word_defn_edit(wdl_id, word_defn_id):
    wdl = WordDefnList.get_by_id(wdl_id)
    word_defn = WordDefn.get_by_id(word_defn_id)
    
    pos_list = 'noun', 'pronoun', 'verb', 'adjective', 'adverb', 'preposition', 'conjunction', 'interjection'
    if request.method == "GET":
        print(word_defn.defn)
        return render_template("word_defn_edit.html", word_defn=word_defn, pos_list=pos_list, wdl=wdl)

    else:
        word = request.form.get("word", "")
        pos = request.form.get("pos", "")
        defn = request.form.get("defn", "")
        example1 = request.form.get("example1", "")
        example2 = request.form.get("example2", "")
        example3 = request.form.get("example3", "")
        examples = []

        if example1 != None:
            examples.append(example1)
        if example2 != None:
            examples.append(example2)
        if example3 != None:
            examples.append(example3)

        word_defn = WordDefn.update(word, pos, defn, examples, word_defn.id)
        return redirect(f"/word-definition-list/{wdl.id}")


@app.route("/word-definition/<wdl_id>/<word_defn_id>/delete", methods=['GET', 'POST'])
def word_defn_delete(wdl_id, word_defn_id):
    wdl = WordDefnList.get_by_id(wdl_id)
    word_defn = WordDefn.get_by_id(word_defn_id)

    if request.method == "GET":
        return render_template("word_defn_delete.html", wdl=wdl, word_defn=word_defn)
    else:
        delete_map_of_word_defn_to_list(word_defn_id, wdl_id)
        delete_word_defn(word_defn_id)
        return redirect(f"/word-definition-list/{wdl.id}")


@app.route("/word-definition-list/<wdl_id>/launch-practice")
def word_defn_list_launch_practice(wdl_id):
    word_defn_ids = get_word_defns_from_list(wdl_id)
    user_id = WordDefnList.get_user_by_wdl_id(wdl_id)
    session = PracticeSession.create(user_id, wdl_id, word_defn_ids)
    return redirect(f"/word-definition-list/{wdl_id}/practice/{session.id}")


@app.route("/word-definition-list/<wdl_id>/practice/<session_id>")
def word_defn_list_practice(wdl_id, session_id):
    wdl = WordDefnList.get_by_id(wdl_id)
    session = PracticeSession.get_by_id(session_id)
    return render_template("wdl_practice.html", wdl=wdl, session=session)

if __name__ == "__main__":
    app.run(debug=True, port=8080)