import json

import datefinder
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker

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
    if word in stop_words:
        return ''
    if word in global_abbr:
        return global_abbr[word]
    correction = spell.correction(word)
    if correction:
        word = correction
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
