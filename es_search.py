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


FALSE = ['omg that is not related', '2017 2017 2017', '''What takes people so long to order at Panera Bread? It's like the people in front of me are ordering in Morse code''',
        'My dear Barry, thank you for that lovely pic. You reminded me great moments. Your CD, your songs, your music, but the best your voice.',
        '''#wallofsport news: chelsea's antonio rudiger: i joined club because of antonio conte https://t.co/avo5zli2ne''',
        '[to read] searching for the best hotels lincoln city oregon https://t.co/giv9fmwaj0',
        'good morning friends.... after long time again came to wb.... its like returning in to the ocean of joy.',
        '''we're #hiring! click to apply: maintenance technician - tire care - https://t.co/kfpedznzdp #automotive #meadowview, va #job #jobs''',
        '''"each wrinkle and line is to show life's wonderful and more difficult points in time wherein our moments of laught…… https://t.co/qj5jowktdg''']

TRUE = ['i am ordering sweet roll at panera bread', 'we just ordered pizza at panera bread', 'side effect of the HPV vaccine is headache',
        'my visit to Petra was amazing i highly recommend to the see the cave this tour is a must',
        'Everyone will tell you that you need a minimum for 2-4 days in Petra but do you really?! Find out what we recommend https://goo.gl/VYQQeN ',
        'Got to the bridge &, like so many songs, smt reminded me of barry manilow version of "Could It Be Magic," one of the best pop songs ever.',
        '''hoppy sour: citra by almanac beer company found at stubby's gastropub. your new best friend.''',
        'The 10 best Barry Manilow songs',
        'Barry your songs are the best gift ever. I remember my mom and I singing *badly Mandy in the car. Thanks']


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

    def search_topics(self, query, threshold=14):
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
            title = topic["title"].lower()
            print title
            title_babelfy = babelfy_query(title)
            print title_babelfy
            self.es.index(index=self.index, doc_type='topics', id=topic['topid'],
                          body={'title': title,
                                'title_babelfy': title_babelfy,
                                'description_stem': description,
                                'narrative_stem': narrative,
                                'description': topic["description"].lower(),
                                'narrative': topic["narrative"].lower()
                                })


def load_topics_in_ES(file, index_name):
    topics_json = json.load(open(file))
    es = ESClient(index=index_name)
    es.load_sample_topics(topics_json)


def test_search(debug=True):
    es = ESClient(index='trec17sample')
    for tweet in FALSE:
    # for tweet in SAMPLE_TWEETS:
        results = es.search_topics(query=tweet)
        report_results(tweet, results, es)
        if results:
            print 'Tweet:', tweet
            print "Error FP!"
    for tweet in TRUE:
        # tweet = twokenize(tweet)
        # print tweet
    # for tweet in SAMPLE_TWEETS:
        if debug:
            results = es.search_topics(query=tweet, threshold=0)
            report_results(tweet, results, es)
        else:
            results = es.search_topics(query=tweet)
        if not results:
            print 'Tweet:', tweet
            print "Error TP!"
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


def load_topics_from_file(i=0):
    # 0 for training topics, 1 for production
    load_topics_in_ES(TOPIC_FILES[i], INDICES[i])


def test_duplicate_detection():
    # TODO ??
    tweet1 = 'omg that is not related anyway wtf'
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
    test_duplicate_detection()
    # test_titles_search()

    # test_search()

    # results = es.count(query='panera Bread')
    # print results['count']
