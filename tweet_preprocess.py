# -*- coding: utf-8 -*-
'''
svakulenko
16 July 2017
'''

import re
import string
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer

from twokenize import tokenizeRawTweetText, punctSeq


SAMPLE_TWEETS = [ 
                '''@darlene_a_10101 nice try, but no. just a person who knows we live by the rule of law. not the rule of what you think should be.''',
                '''there's a way to do both... lol https://t.co/tqtiraqbgx''',
                '''2017 world series jodie whittaker was amazing in @broadchurchtv. super excited to watch #doctor13 😁''',
                '''2017 world series ''',
# 23l portable electric stainless steel countertop oven caravan boat 2 hotplate... - https://t.co/z9e2fdcigu
# my love,  my kiss, my heart#bama2017_superjunior#bama2017_superjunior#bama2017_superjunior
# les dawson - "unforgettable" &amp; mother in law https://t.co/uyiibniykc via @youtube
# @dearanathema i am,, sorry
                ]


def regex_based(text):

    # translate_table = dict((ord(char), None) for char in string.punctuation)

    #####remove hashtag#####
    clean_text = re.sub(r'#[^\s]+', '', text)
    #####remove @ #####
    clean_text = re.sub(r'@[^\s]+', '', clean_text)
    #####remove all term behind http#####
    clean_text = re.sub(r'http\S+', '', clean_text)
    # re.sub(r"(?:\@|https?\://)\S+", "", doc)
    # remove redundant spaces
    # clean_text = clean_text.strip()
    # print clean_text
    # remove punctuation
    # clean_text = clean_text.translate(translate_table)

    return clean_text


def twokenize(text):
    clean_text = re.sub(r"(?:\@|https?\://)\S+", "", text)

    # Remove documents with less 100 words (some tweets contain only URLs)
    # documents = [doc for doc in documents if len(doc) > 100]

    # Tokenize
    tokens = tokenizeRawTweetText(clean_text.lower())
    # print documents

    # Remove stop words
    # unigrams = [w for doc in documents for w in doc if len(w) == 1]
    # bigrams = [w for doc in documents for w in doc if len(w) == 2]
    # print bigrams
    stoplist = set(nltk.corpus.stopwords.words("english"))
        # + STOPLIST_TW + STOPLIST + unigrams + bigrams)
    # and strip #
    tokens = [token.lstrip('#') for token in tokens if token not in stoplist]
    # print tokens
    # remove punctuation tokens
    tokens = [token for token in tokens if not re.match(punctSeq, token)]

    # lmtzr = WordNetLemmatizer()
    # tokens = [lmtzr.lemmatize(token) for token in tokens]

    stemmer = SnowballStemmer("english")
    tokens = [stemmer.stem(token) for token in tokens]

    clean_text = ' '.join(tokens)
    return clean_text


def stem(text):
    return " ".join()



def test_tweet_preprocess(preprocess_function):
    for tweet in SAMPLE_TWEETS:
        print preprocess_function(tweet)


if __name__ == '__main__':
    # test_tweet_preprocess(regex_based)
    test_tweet_preprocess(twokenize)