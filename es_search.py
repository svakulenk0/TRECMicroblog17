'''
svakulenko
14 july 2017
'''
import json
from elasticsearch import Elasticsearch
from mappings import *
from tweet_preprocess import twokenize


INDEX = 'trec17sample'
FALSE = ['sweet roll of course maybe is best at panera bread', '2017', '2017 world series', '2017 world series today',
                  'i am at panera bread']
TRUE = ['i am ordering sweet roll at panera bread', 'we just ordered pizza at panera bread', 'side effect of the HPV vaccine is headache',
        'my visit to Petra was amazing i highly recommend to the see the cave this tour is a must']

class ESClient():

    def __init__(self, index):
        self.es = Elasticsearch()
        self.index = index

    def count(self, query, threshold=10):
        return self.es.count(index=self.index, q=query, min_score=threshold)

    def search(self, query, threshold=15):
        query = twokenize(query)
        # print query
        results = self.es.search(index=self.index, q=query, doc_type='topics', analyzer='english')['hits']
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
            narrative = twokenize(topic['narrative'])
            self.es.index(index=self.index, doc_type='topics', id=topic['topid'],
                          body={'title': topic["title"].lower(),
                                'description_stem': description,
                                'narrative_stem': narrative,
                                'description': topic["description"].lower(),
                                'narrative': topic["narrative"].lower()
                                })


def load_sample_topics():
    topics_json = json.load(open('data/TREC2017-RTS-topics1.json'))
    es = ESClient(index='trec17sample')
    es.load_sample_topics(topics_json)


def test_search(debug=False):
    es = ESClient(index='trec17sample')
    for tweet in FALSE:
    # for tweet in SAMPLE_TWEETS:
        results = es.search(query=tweet)
        # report_results(tweet, results, es)
        if results:
            print "Error!"
            print 'Tweet:', tweet
    for tweet in TRUE:
        # tweet = twokenize(tweet)
        # print tweet
    # for tweet in SAMPLE_TWEETS:
        if debug:
            results = es.search(query=tweet, threshold=0)
            report_results(tweet, results, es)
        else:
            results = es.search(query=tweet)
        if not results:
            print tweet
            print "Error!"
            print results


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


if __name__ == '__main__':
    # load_sample_topics()
    # test_titles_search()

    test_search()

    # results = es.count(query='panera Bread')
    # print results['count']
