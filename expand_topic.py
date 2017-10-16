# -*- coding: utf-8 -*-
'''
svakulenko
25 july 2017
'''

from conceptualization import lotus_recursive_call, lookup_nns, loop_concept_expansion
from process_tweets import segment_on_stopwords
from tweet_preprocess import MYSTOPLIST


TOPIC = {
           "narrative" : "The user is an avid cycler and wants to follow any injuries to riders in this year's Tour de France race.",
           "title" : "Tour de France",
           "topid" : "RTS138",
           "description" : "What injuries happened in this year's Tour de France?"
        }


def discover_topic(topic=TOPIC):
    description = topic['description']
    print description

    # preprocesss description
    # remove stopwords
    description = description.split(" ")  # .lower()
    description = " ".join([token for token in description if token not in MYSTOPLIST])
    print description
    
    topic_concepts = lotus_recursive_call(description, filter_ns=False, size=10)
    print topic_concepts
    
    for concept_uri in topic_concepts:
        concepts, descriptions = loop_concept_expansion(concept_uri)
        for hop in descriptions:
            for description in hop:
                print description


def process_topic_description(topic=TOPIC, tokenize=segment_on_stopwords):
    title = topic['title']
    print title
    
    topic_concepts = lotus_recursive_call(title, filter_ns='dbpedia', size=10)
    
    for concept_uri in topic_concepts:
        concepts, descriptions = loop_concept_expansion(concept_uri)
        for hop in descriptions:
            for description in hop:
                print description
                tokens = tokenize(description)
                print '\n'
                print tokens
                print '\n'
                for token in tokens:
                    lotus_recursive_call(token, verbose=True, size=2, filter_ns='dbpedia')
                print '\n'


if __name__ == '__main__':
    discover_topic()
    # process_topic_description()

