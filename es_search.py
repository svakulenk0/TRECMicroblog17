'''
svakulenko
14 july 2017
'''
import json
from elasticsearch import Elasticsearch
from mappings import *


INDEX = 'trec17sample'
SAMPLE_QUERIES = ['panera bread', '2017', '2017 world series']

class ESClient():

    def __init__(self, index):
        self.es = Elasticsearch()
        self.index = index

    def count(self, query, threshold=10):
        return self.es.count(index=self.index, q=query, min_score=threshold)

    def search(self, query):
        return self.es.search(index=self.index, q=query)['hits']

    def search_titles(self, query, threshold=10):
        '''
        implements exact search on the topics' title field
        '''
        results = self.es.search(index=self.index, body={"query": {"term": {"title": query}}})['hits']
        # if results['max_score'] > threshold:
        #     return results['hits']
        return results

    def load_sample_topics(self, topics_json):
        # delete previous index
        self.es.indices.delete(index=self.index, ignore=[400, 404])
        # define mapping
        self.es.indices.create(index=self.index, ignore=400, body=mapping_exact_title)
        for topic in topics_json:
            # print topic['title']
            self.es.index(index=self.index, doc_type='topics', id=topic['topid'],
                          body={'title': topic["title"].lower(),
                                'description': topic["description"].lower(),
                                'narrative': topic["narrative"].lower()
                                })


def load_sample_topics():
    topics_json = json.load(open('data/TREC2017-RTS-topics1.json'))
    es = ESClient(index='trec17sample')
    es.load_sample_topics(topics_json)


def test_search():
    es = ESClient(index='trec17sample')
    for tweet in SAMPLE_QUERIES:
        results = es.search(query=tweet)
        report_results(tweet, results)


def report_results(tweet, results):
    if results['hits']:
        print 'Tweet:', tweet
        print 'Topic:', results['hits'][0]['_source']['title']
        print results['hits'][0]['_source']['description']
        print '\n'


def test_titles_search(text='panera bread'):
    es = ESClient(index='trec17sample')
    for tweet in SAMPLE_QUERIES:
        results = es.search_titles(query=tweet)
        report_results(tweet, results)


if __name__ == '__main__':
    # load_sample_topics()
    test_titles_search()
    
    # test_search()
    # results = es.count(query='panera Bread')
    # print results['count']
