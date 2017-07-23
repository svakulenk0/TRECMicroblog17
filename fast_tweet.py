'''
svakulenko
23 july 2017
'''
import json
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity
import fasttext

from settings import *


EMBEDDINGS_MODEL_PATH = 'embeddings/fasttext/fil9.bin'


def encode_topics(model, file=TOPICS):
    '''
    Vectorize topics with fasttext
    '''
    topic_vectors = {}

    with open(file, "r") as f:
        topics_json = json.load(f)
        for topic in topics_json:
            title = topic['title']
            # print title
            # embed titles with fasttext
            topic_vectors[title] = np.array(model[title])

    return topic_vectors


def find_relevant_topic(tweet, topic_vectors, model, similarity_threshold=0):
    tweet_vector = np.array(model[tweet])
    nn = None
    max_cosine = 0
    for title, topic_vector in topic_vectors.items():
        cosine = cosine_similarity(tweet_vector.reshape(1, -1), topic_vector.reshape(1, -1))[0][0]
        if cosine > max_cosine:
            nn = title
            max_cosine = cosine
    print max_cosine
    if max_cosine > similarity_threshold:
        print nn


def main():
    tweet = 'HPV vaccine'
    # load fasttext model
    model = fasttext.load_model(EMBEDDINGS_MODEL_PATH)
    topic_vectors = encode_topics(model)
    find_relevant_topic(tweet, topic_vectors, model)


if __name__ == '__main__':
    main()
