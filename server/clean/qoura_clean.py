import datetime
import json

import datefinder
import ir_datasets
import nltk
import pandas as pd
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from spellchecker import SpellChecker

dataset = ir_datasets.load("beir/quora/dev")

queries = pd.DataFrame(dataset.queries_iter())
docs = pd.DataFrame(dataset.docs)
qrels = pd.DataFrame(dataset.qrels_iter())

queries = queries.fillna('')
docs = docs.fillna('')
qrels = qrels.fillna('')

queries.to_csv("../resources/qoura/qoura_queries.csv", index=False)
docs.to_csv("../resources/qoura/qoura_docs.csv", index=False)
qrels.to_csv("../resources/qoura/qoura_qrels.csv", index=False)

queries = pd.read_csv("../resources/qoura/qoura_queries.csv")
docs = pd.read_csv("../resources/qoura/qoura_docs.csv")
qrels = pd.read_csv("../resources/qoura/qoura_qrels.csv")

vectorizer = TfidfVectorizer(stop_words='english')
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
spell = SpellChecker()
translation_table = {
    48: " zero ",  # 0
    49: " one ",  # 1
    50: " two ",  # 2
    51: " three ",  # 3
    52: " four ",  # 4
    53: " five ",  # 5
    54: " six ",  # 6
    55: " seven ",  # 7
    56: " eight ",  # 8
    57: " nine ",  # 9
    33: ' ',  # !
    34: ' ',  # "
    35: ' ',  # #
    36: ' ',  # $
    37: ' ',  # %
    38: ' ',  # &
    39: ' ',  # '
    40: ' ',  # (
    41: ' ',  # )
    42: ' ',  # *
    43: ' ',  # +
    44: ' ',  # ,
    45: ' ',  # -
    46: ' ',  # .
    47: ' ',  # /
    58: ' ',  # :
    59: ' ',  # ;
    60: ' ',  # <
    61: ' ',  # =
    62: ' ',  # >
    63: ' ',  # ?
    64: ' ',  # @
    91: ' ',  # [
    92: ' ',  # \
    93: ' ',  # ]
    94: ' ',  # ^
    95: ' ',  # _
    96: ' ',  # `
    123: ' ',  # {
    124: ' ',  # |
    125: ' ',  # }
    126: ' ',  # ~
}
global_abbr = json.load(open("../resources/jsons/global-abbr.json"))


def pos_tagger(nltk_tag):
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def lemmatize_word(word):
    if (word in stop_words): return ''
    if (word in global_abbr): return global_abbr[word]
    correction = spell.correction(word)
    if (correction): word = correction
    tokens = nltk.word_tokenize(word)
    pos_tagged = nltk.pos_tag(tokens)
    tag = pos_tagger(pos_tagged[0][1])
    if tag is None:
        return tokens[0]
    else:
        return lemmatizer.lemmatize(tokens[0], tag)


def get_lemmatize_texts(texts):
    texts = [" ".join([
        match.strftime("%Y-%m-%d")
        for match in datefinder.find_dates(text, strict=True)
    ]) + " " + " ".join([
        lemmatize_word(word)
        for word in str(text).lower().translate(translation_table).split()
        if word not in stop_words
    ]) for text in texts]
    return texts


def clean_queries(queries):
    print("Clean queries begin in : " + str(datetime.datetime.now()))
    queries['lemmatized_text'] = get_lemmatize_texts(queries['text'])
    queries = queries.fillna('')
    queries.to_csv("../resources/qoura/qoura_queries_clean.csv", index=False)
    print("Clean queries end in : " + str(datetime.datetime.now()))


def clean_docs(docs):
    print("Clean docs begin in : " + str(datetime.datetime.now()))
    docs['lemmatized_text'] = get_lemmatize_texts(docs['text'])
    docs = docs.fillna('')
    docs.to_csv("../resources/qoura/qoura_docs_clean.csv", index=False)
    print("Clean docs end in : " + str(datetime.datetime.now()))


if __name__ == '__main__':
    clean_queries(queries)  # to clean queries      (takes about 2 minutes)
    clean_docs(docs)  # to clean docs         (takes about 6 hours)
