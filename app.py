"""
A dictionary is created. Each key is a word and the corresponding value is a list of synsets that has the word. When the code is run, a 
random word and its information will be printed
"""
from flask import Flask, make_response, render_template, request, redirect
app = Flask(__name__)

import random
syn_dict = {}

class Synset():
    def __init__(self, lex_id=00, syn_id="",  part_of_speech="", words=None, occurrences=None, definitions=None, sentences=None):
        self.lex_id = lex_id
        self.syn_id = syn_id
        self.part_of_speech = part_of_speech
        self.words = words or list()
        self.occurrences = occurrences or list()
        self.definitions = definitions or list()
        self.sentences = sentences or list()


def dictionary_creater():
    for part_of_speech in ["noun", "verb", "adj", "adv"]:
        f = open("./WordNet-3.0/dict/data." + part_of_speech)
        for line in f:
            if line[0] != " ":
                syn = Synset()
                line = line[:-3]

                #lex_id
                syn.lex_id = int(line[9:11])

                #syn_id
                syn.syn_id = line[0:8] + " " + part_of_speech

                #part_of_speech
                syn.part_of_speech = part_of_speech

                #words
                num_of_words = line[14:16]
                num_of_words = int(num_of_words, 16)
                split_line = line[17:].split(' ')

                for i in range(0, num_of_words*2):
                    if i%2 == 0:
                        syn.words.append(split_line[i])
                    else:
                        occurrence = int(split_line[i], 16)
                        syn.occurrences.append(occurrence)

                #definitions and sentance usage
                split_line = line.split("| ")
                split_line = split_line[1].split("; ")
                for sentence in split_line:
                    if len(sentence) != 0:
                        if sentence[0] == '"':
                            syn.sentences.append(sentence)
                        else:
                            syn.definitions.append(sentence)

                #adding to the dictionary
                for word in syn.words:
                    if word not in syn_dict:
                        syn_dict[word] = []

                    syn_dict[word].append(syn)


#arranging the synsets in order
def synset_comparison_key(word):
    def _synset_comparison_key(syn):
        part_of_speech = syn.syn_id[9:]
        if part_of_speech == "noun":
            base = 100
        elif part_of_speech == "verb":
            base = 200
        elif part_of_speech == "adj":
            base = 300
        elif part_of_speech == "adv":
            base = 400

        index = syn.words.index(word)
        base += syn.occurrences[index]
        return base
    
    return _synset_comparison_key


#calls the function to sort the synsets
def synset_sorter(word):
    synsets = syn_dict[word]
    synsets = sorted(synsets, key=synset_comparison_key(word))
    return synsets


dictionary_creater()
@app.route("/")
def home():
    rand_word = random.choice(list(syn_dict))
    display_word = rand_word.replace("_", " ")
    synsets = synset_sorter(rand_word)
    return render_template("word.html", word=display_word, synsets=synsets)

@app.route("/search")
def search():
    word = request.args.get("word", "")
    word = word.lower()
    if word == "":
        return redirect("/")

    synsets = synset_sorter(word)
    display_word = word.replace("_", " ")
    return render_template("word.html", word=display_word, synsets=synsets)