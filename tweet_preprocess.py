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

from twokenize import tokenizeRawTweetText
from stoplist_twitter import STOPLIST_TW

SAMPLE_TOPICS = ['Information concerning possible side effects of the HPV vaccine']

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

stoplist = set(nltk.corpus.stopwords.words("english") + STOPLIST_TW)


def regex_based(text):

    # translate_table = dict((ord(char), None) for char in string.punctuation)

    #####remove hashtag#####
    clean_text = re.sub(r'#[^\s]+ ', '', text)
    #####remove @ #####
    clean_text = re.sub(r'@[^\s]+ ', '', clean_text)
    #####remove all term behind http#####
    clean_text = re.sub(r'http\S+ ', '', clean_text)
    # re.sub(r"(?:\@|https?\://)\S+", "", doc)
    # remove redundant spaces
    # clean_text = clean_text.strip()
    # print clean_text
    # remove punctuation
    clean_text = re.sub(r'[^a-zA-Z ]', '', clean_text)

    tokens = [token for token in clean_text.split(' ') if token not in stoplist]
    # clean_text = ' '.join(set(tokens))
    clean_text = ' '.join(tokens)

    return clean_text


def twokenize(text, no_duplicates=True, stem=True):
    clean_text = re.sub(r"(?:\@|https?\://)\S+", "", text)

    # remove non alpha chars
    # clean_text = filter(str.isalnum, clean_text)
    # regex = re.compile('[^a-zA-Z ]')
    # clean_text = regex.sub('', clean_text)
    clean_text = re.sub(r'[^\x00-\x7F]+',' ', clean_text)
    # strip punctuation
    # clean_text = clean_text.decode('unicode_escape').encode('ascii','ignore')
    translator = string.maketrans(string.punctuation, ' '*len(string.punctuation)) #map punctuation to space
    clean_text = str(clean_text).translate(translator)

    # Remove documents with less 100 words (some tweets contain only URLs)
    # documents = [doc for doc in documents if len(doc) > 100]

    # Tokenize
    # tokens = tokenizeRawTweetText(clean_text.lower())
    tokens = tokenizeRawTweetText(clean_text)

    # Remove stop words
    # unigrams = [w for doc in documents for w in doc if len(w) == 1]
    # bigrams = [w for doc in documents for w in doc if len(w) == 2]
    # print bigrams
        # + STOPLIST_TW + STOPLIST + unigrams + bigrams)
    # and strip #
    tokens = [token for token in tokens if token not in stoplist]
    # tokens = [token for token in tokens if token not in string.punctuation]
    # print tokens
    # remove punctuation tokens
    # tokens = [token for token in tokens if not re.match(punctSeq, token)]

    # lmtzr = WordNetLemmatizer()
    # tokens = [lmtzr.lemmatize(token) for token in tokens]
    if stem:
        stemmer = SnowballStemmer("english")
        # print tokens
        tokens = [stemmer.stem(token) for token in tokens]
    if no_duplicates:
        # tokens = set(tokens)
        tokens = f7(tokens)
    clean_text = ' '.join(tokens)
    return clean_text


def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def test_tweet_preprocess(preprocess_function, tweet):
    # for tweet in SAMPLE_TWEETS:
    print preprocess_function(tweet)


if __name__ == '__main__':
    # test_tweet_preprocess(regex_based)
    test_tweet_preprocess(twokenize, tweet='''we just ordered pizza at panera bread?''')