class WordMeaning(object):
    def __init__(self, word):
        self.word = word
        self.word_lexical_categories = []

class WordLexicalCategory(object):
    def __init__(self, word, lexical_category, pronunciation_audio, phonetic_spelling, etymologies):
        self.word = word
        self.lexical_category = lexical_category
        self.pronunciation_audio = pronunciation_audio
        self.phonetic_spelling = phonetic_spelling
        self.etymologies = etymologies
        self.word_definitions = []

class WordDefinition(object):
    def __init__(self, definition_id, definitions, examples, synonyms):
        self.id = id
        self.definitions = definitions
        self.examples = examples
        self.synonyms = synonyms


def word_meaning_builder(word, data):
    word_meaning = WordMeaning(word)
    results = data["results"][0]
    lexicalEntries = results["lexicalEntries"]

    for lexical_entry in lexicalEntries:
        lexical_category = lexical_entry["lexicalCategory"]["id"]

        #for each category (verb, noun, etc.)
        entry = lexical_entry["entries"][0]

        #etymologies
        etymologies = entry.get("etymologies", [])

        #pronunciation
        pronunciation = entry.get("pronunciations", [])
        pronunciation_audio, phonetic_spelling = None, None
        for pronun in pronunciation:
            if "audioFile" in pronun:
                pronunciation_audio = pronun["audioFile"]
                phonetic_spelling = pronun["phoneticSpelling"]
                break
        
        #creates an object of the WordLexicalCategory class and adds it to the list of lexical categoryies in the WordMeaning class
        word_lexical_category = WordLexicalCategory(word, lexical_category, pronunciation_audio, phonetic_spelling, etymologies)
        word_meaning.word_lexical_categories.append(word_lexical_category)
        
        #inner dictionary
        senses = entry["senses"]
        for sense in senses:
            #id of the definition
            definition_id = sense["id"]
            
            #actual definition
            definitions = sense["definitions"]

            #examples
            examples = []
            for example in sense.get("examples", []):
                examples.append(example["text"])

            #synonyms
            synonyms = []
            for synonym in sense.get("synonyms", []):
                synonyms.append(synonym["text"])

            word_definition = WordDefinition(definition_id, definitions, examples, synonyms)
            word_lexical_category.word_definitions.append(word_definition)

    return word_meaning