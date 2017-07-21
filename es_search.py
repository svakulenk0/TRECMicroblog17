# -*- coding: utf-8 -*-
'''
svakulenko
14 july 2017
'''
import json
from elasticsearch import Elasticsearch

from settings import *
from mappings import *
from tweet_preprocess import twokenize
from conceptualization import babelfy_query
from queries import multi_weighted


FALSE = [
            '''wand hes show long fact need world joze cole hate best''',
            '''noida lead provid cheap india websit design respons compani best''',
            '''s''',
            '''cranston bryan notaaron show ruin itnevr actor side wher amp paul charact think bettr''',
            '''album ankur fre song tyagi ts music snake shadi come fact shook''',
            '''great good woman make thing doesnt take man''',
            '''korea north world rao visit honest bbc santosh moral consid respons news''',
            '''dizoard mountain le franc rider tour col conquer var final stage''',
            '''plate menu review swindian hey know interest editori small'''
        ]

TRUE = [
            '''The best beach in the world is in Australia near the coral reef'''
       ]


class ESClient():

    def __init__(self, index):
        self.es = Elasticsearch()
        self.index = index

    def count(self, query, threshold=10):
        return self.es.count(index=self.index, q=query, min_score=threshold)

    def search_tweets(self, query, threshold=15):
        results = self.es.search(index=self.index, q=query, doc_type='tweets')['hits']
        if results['max_score'] > threshold:
            return results['hits'][0]
        return None

    def search_topics(self, query, threshold=10, explain=False):
        # print query
        request = multi_weighted
        request['query']['multi_match']['query'] = query
        # results = self.es.search(index=self.index, q=query, doc_type='topics', analyzer='english', explain=explain, size=1)['hits']
        results = self.es.search(index=self.index, body=request, doc_type='topics', explain=explain, size=1)['hits']
        if results['max_score'] > threshold:
            return results['hits'][0]
        return None

    def search_titles(self, query, threshold=5):
        '''
        implements exact search on the topics' title field
        '''
        results = self.es.search(index=self.index, body={"query": {"match": {"title": query}}})['hits']
        if results['max_score'] > threshold:
            return results['hits'][0]
        return None

    def store_tweet(self, topic_id, tweet_text):
        self.es.index(index=self.index, doc_type='tweets', id=topic_id,
                      body={'tweet': tweet_text
                            })

    def load_sample_topics(self, topics_json):
        # delete previous index
        self.es.indices.delete(index=self.index, ignore=[400, 404])
        # define mapping
        self.es.indices.create(index=self.index, ignore=400, body={})
        for topic in topics_json:
            description = twokenize(topic['description'])
            description = twokenize(topic['description'])
            narrative = twokenize(topic['narrative'])
            title = twokenize(topic['title'])
            print title
            # title_babelfy = babelfy_query(title)
            # print title_babelfy
            self.es.index(index=self.index, doc_type='topics', id=topic['topid'],
                          body={'title': topic["title"].lower(),
                                'title_stem': title,
                                # 'title_babelfy': title_babelfy,
                                'description_stem': description,
                                'narrative_stem': narrative,
                                'description': topic["description"].lower(),
                                'narrative': topic["narrative"].lower()
                                })


def load_topics_in_ES(file, index_name):
    topics_json = json.load(open(file))
    es = ESClient(index=index_name)
    es.load_sample_topics(topics_json)


def test_search(debug=False, explain=False):
    es = ESClient(index='trec17sample')
    nerrors = 0
    for query in FALSE:
    # for tweet in SAMPLE_TWEETS:
        # tweet = twokenize(tweet)
        if debug:
            results = es.search_topics(query=query, threshold=0, explain=explain)
            report_results(query, results, es)
        else:
            results = es.search_topics(query=query)
            if results:
                print 'Query:', query
                print "Error FP!"
                nerrors += 1

    for tweet in TRUE:
        query = twokenize(tweet)
        # print tweet
    # for tweet in SAMPLE_TWEETS:
        if debug:
            results = es.search_topics(query=query, threshold=0, explain=explain)
            report_results(query, results, es)
        else:
            results = es.search_topics(query=query)
            if not results:
                print 'Query:', query
                print "Error FN!"
                print results
                nerrors += 1

    print '#Errors: ', nerrors


def report_results(tweet, results, es):
    print 'Tweet:', tweet

    if results:
        print results
        print 'Topic:', results['_source']['title']
        print results['_source']['description']
        # store tweet in ES
        # es.store_tweet(results['hits'][0]['_id'], tweet)
    else:
        print 'Did not match'
    print '\n'


# def test_titles_search():
#     es = ESClient(index='trec17sample')
#     for tweet in FALSE:
#     # for tweet in SAMPLE_TWEETS:
#         results = es.search_titles(query=tweet)
#         # report_results(tweet, results, es)
#         if results:
#             print "Error!"
#             print 'Tweet:', tweet
#     for tweet in TRUE:
#     # for tweet in SAMPLE_TWEETS:
#         results = es.search_titles(query=tweet)
#         report_results(tweet, results, es)
#         if not results:
#             print "Error!"
#             print results


def load_topics_from_file(i=0):
    # 0 for training topics, 1 for production
    load_topics_in_ES(SAMPLE_TOPICS[i], TEST_INDEX)


def test_duplicate_detection():
    # TODO ??
    tweet1 = 'omg that is not related'
    tweet2 = 'omg that is not related'

    # preprocess tweets
    # tweet1 = twokenize(tweet1)
    # tweet2 = twokenize(tweet2)

    print tweet1
    print tweet2

    es = ESClient(index='trec17sample')
    # store tweet in ES
    es.store_tweet('test2', tweet1)
    # check duplicates
    duplicates = es.search_tweets(query=tweet2)
    print duplicates
    assert duplicates
    if duplicates:
        print 'Duplicate!'


if __name__ == '__main__':
    # test_duplicate_detection()
    # test_titles_search()
    # load_topics_from_file()

    test_search()

    # results = es.count(query='panera Bread')
    # print results['count']
