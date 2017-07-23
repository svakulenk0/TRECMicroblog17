# -*- coding: utf-8 -*-
'''
svakulenko
23 july 2017

First run encode_topics to save topic embeddings in file
Then main
'''
import json
import numpy as np
import pickle

from sklearn.metrics.pairwise import cosine_similarity
import fasttext

from settings import *
from utils import load_titles
from sample_tweets import TRUE, FALSE
from tweet_preprocess import twokenize


EMBEDDINGS_MODEL_PATH = './embeddings/fasttext/fil9.bin'

EMBEDDED_TOPICS_PATH = './data/fasttext_topics17.pkl'
EMBEDDED_TOPIC_TITLES_PATH = './data/fasttext_topic_titles17.pkl'


def embed_titles(infile=TOPICS, outfile=EMBEDDED_TOPIC_TITLES_PATH):
    '''
    Vectorize topics with fasttext and save to file
    ntopic=188, embeddings_dim=100
    '''
    with open(infile, "r") as f:
        topics_json = json.load(f)

    topic_titles = []
    topic_vectors = []

    model = fasttext.load_model(EMBEDDINGS_MODEL_PATH)

    for i, topic in enumerate(topics_json):
        title = topic['title']
        # title = topic['title']
        # title = topic['title']
        # print title
        topic_titles.append(title)
        # embed titles with fasttext
        topic_vectors.append(model[title])

    assert len(topic_vectors) == len(topic_titles)

    with open(outfile, 'w') as f:
        pickle.dump(topic_vectors, f)

    return topic_titles, topic_vectors


def embed_topics(infile=TOPICS, outfile=EMBEDDED_TOPICS_PATH):
    '''
    Vectorize topics with fasttext and save to file
    ntopic=188, embeddings_dim=100
    '''
    with open(infile, "r") as f:
        topics_json = json.load(f)

    topic_vectors = []

    model = fasttext.load_model(EMBEDDINGS_MODEL_PATH)

    for i, topic in enumerate(topics_json):
        title = topic['title']
        description = topic['title']
        narrative = topic['title']

        joint = " ".join([title, description, narrative])
        # embed topics with fasttext
        topic_vectors.append(model[joint])

    assert len(topic_vectors) == len(topics_json)

    with open(outfile, 'w') as f:
        pickle.dump(topic_vectors, f)


class FastTweet():
    '''
    Retrieves topics similar to tweet
    '''

    def __init__(self, model_path=EMBEDDINGS_MODEL_PATH,
                 embeddings_path=EMBEDDED_TOPICS_PATH):
        # load fasttext model
        self.model = fasttext.load_model(model_path)
        # load topic titles
        self.topic_titles = load_titles()
        # load topic embeddings
        with open(embeddings_path, 'r') as f:
            self.topic_vectors = pickle.load(f)

    def find_relevant_topic(self, tweet, similarity_threshold=0):
        # embed tweet with fasttext model
        tweet_vector = np.array(self.model[tweet]).reshape(1, -1)
        similarities = cosine_similarity(tweet_vector, self.topic_vectors)[0]
        assert len(similarities) == len(self.topic_titles)
        return self.topic_titles[np.argmax(similarities)], max(similarities)

    def find_relevant_topics(self, tweets, similarity_threshold=0, preprocess=False):
        # embed tweets with fasttext model
        tweets_vectors = []
        for tweet in tweets:
            if preprocess:
                tweet = preprocess(tweet)
            tweets_vectors.append(self.model[tweet])

        assert len(tweets_vectors) == len(tweets)

        similarities = cosine_similarity(tweets_vectors, self.topic_vectors)

        assert len(similarities) == len(tweets)

        titles = [self.topic_titles[np.argmax(similarity)] for similarity in similarities]
        scores = [max(similarity) for similarity in similarities]

        return titles, scores


def test_with_preprocessing(preprocess=twokenize):
    '''
    Test on sample tweets
    '''
    ft = FastTweet()


    tweets = [preprocess(tweet) for tweet in TRUE]

    topics, scores = ft.find_relevant_topics(tweets)
    # report results for relevant tweets 
    print "\nTRUE"
    for i, tweet in enumerate(tweets):
        print "%s -> %s %.2f" % (tweet, topics[i], scores[i])
    min_true = min(scores)
    # print "Minimum for TRUE: %.2f" % min_true


    tweets = [preprocess(tweet) for tweet in FALSE]

    topics, scores = ft.find_relevant_topics(tweets)
    # report results for irrelevant tweets 
    print "\nFALSE"
    for i, tweet in enumerate(tweets):
        print "%s -> %s %.2f" % (tweet.decode('utf-8'), topics[i], scores[i])
    max_false = max(scores)
    # print "Maximum for FALSE: %.2f" % max_false

    print "Score threshold: [%.2f, %.2f]" % (max_false, min_true)
    print min_true - max_false
    assert max_false < min_true


def test_find_relevant_topic():
    # sample tweet
    tweet = 'london real estate'
    ft = FastTweet()
    print ft.find_relevant_topic(tweet)


def test_find_relevant_topics():
    # sample tweet
    tweets = ['london real estate', 'iam very irrrelevant here']
    ft = FastTweet()
    print ft.find_relevant_topics(tweets)


def test_without_preprocessing():
    '''
    Test on sample tweets
    '''
    ft = FastTweet()

    topics, scores = ft.find_relevant_topics(TRUE)
    # report results for relevant tweets 
    print "\nTRUE"
    for i, tweet in enumerate(TRUE):
        print "%s -> %s %.2f" % (tweet, topics[i], scores[i])
    min_true = min(scores)
    # print "Minimum for TRUE: %.2f" % min_true
    
    topics, scores = ft.find_relevant_topics(FALSE)
    # report results for irrelevant tweets 
    print "\nFALSE"
    for i, tweet in enumerate(FALSE):
        print "%s -> %s %.2f" % (tweet.decode('utf-8'), topics[i], scores[i])
    max_false = max(scores)
    # print "Maximum for FALSE: %.2f" % max_false

    print "Score threshold: [%.2f, %.2f]" % (max_false, min_true)
    print min_true - max_false
    assert max_false < min_true


if __name__ == '__main__':
    embed_topics()
