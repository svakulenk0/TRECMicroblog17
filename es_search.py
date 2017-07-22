# -*- coding: utf-8 -*-
'''
svakulenko
14 july 2017
'''
import json
from elasticsearch import Elasticsearch

from settings import *
from mappings import *
from tweet_preprocess import twokenize, stoplist
from conceptualization import babelfy_query
# from relevance_feedback import boosting_relevance


TOPIC_SIM_THRESHOLD = 37
# weights for title, description, narrative stemmed fields
# last weight is for the must value
BOOSTS = [3, 2, 1, 4]

DEBUG = False
EXPLAIN = False

multi_weighted = {
                    "query": {
                        "multi_match" : {
                            "type": "most_fields",
                            "fields": ["must^%s" % BOOSTS[-1], "title_stem^%s" % BOOSTS[0], 'description_stem^%s' % BOOSTS[1], 'narrative_stem^%s' % BOOSTS[2]]
                        }
                    }
                 }

multi = {
                    "query": {
                        "multi_match" : {
                            "type": "most_fields",
                            "fields": ["title", 'description', 'narrative']
                        }
                    }
                 }



class ESClient():

    def __init__(self, index):
        self.es = Elasticsearch()
        self.index = index

    def count(self, query, threshold=10):
        return self.es.count(index=self.index, q=query, min_score=threshold)

    def search_tweets(self, query, threshold=3):
        results = self.es.search(index=self.index, body={"query": {"match": {"tweet": query}}}, doc_type='tweets')['hits']
        if results['max_score'] > threshold:
            return results['hits'][0]
        return None

    def search_with_relevance(self, tweet):
        return self.es.search(index=self.index, q=twokenize(tweet), doc_type='topics')['hits']

    # def search_topics(self, query, threshold=TOPIC_SIM_THRESHOLD, explain=False, request=boosting_relevance):
    #     # print query
    #     # request = multi_weighted
    #     request['query']['boosting']['positive']['multi_match']['query'] = query
    #     # request['query']['multi_match']['query'] = query
    #     request['query']['boosting']['negative']['term']['irrelevant'] = query
    #     # results = self.es.search(index=self.index, q=query, doc_type='topics')['hits']
    #     results = self.es.search(index=self.index, body=request, doc_type='topics', explain=explain, size=1)['hits']
    #     if results['max_score'] > threshold:
    #         # check exact match on topic title
    #         topic = results['hits'][0]
    #         title = set(topic['_source']['title_stem'].split(' '))
    #         if title.issubset(set(query.split(' '))):
    #             return topic
    #     return None

    def search_all(self, query, threshold=40, explain=False):
        request = multi
        request['query']['multi_match']['query'] = query
        results = self.es.search(index=self.index, body=request, doc_type='topics', explain=explain)['hits']
        if results['max_score'] > threshold:
        # if results['hits']:
            topic = results['hits'][0]
            title_terms = set(topic['_source']['title_terms'])
            if title_terms.issubset(set(self.tokenize_in_es(query))):
                # print topic['_source']['title']
                return topic
        return None

    def search_all_test(self, query, explain=False):
        request = multi
        request['query']['multi_match']['query'] = query
        return self.es.search(index=self.index, body=request, doc_type='topics', explain=explain)
        # return self.es.search(index=self.index, q=tweet, doc_type='topics', explain=explain)

    def search_titles(self, query, threshold=6, ):
        '''
        implements exact search on the topics' title field
        '''
        results = self.es.search(index=self.index, body={"query": {"match": {"title": query}}})['hits']
        if results['max_score'] > threshold:
        # if results['hits']:
            return results['hits'][0]
        return None

    def search_td(self, query, threshold=6, explain=False):
        '''
        implements exact search on the topics' title field
        '''
        results = self.es.search(index=self.index, explain=explain, body={"query": {"match": {"td": query}}})['hits']
        # if results['max_score'] > threshold:
        if results['hits']:
            return results['hits'][0]
        return None

    def store_tweet(self, topic_id, tweet_text):
        self.es.index(index=self.index, doc_type='tweets', id=topic_id,
                      body={'tweet': tweet_text
                            })

    def positive_relevance(self, topid, text):
        '''
        incorporate positive relevance by writing into a field with high boost
        '''
        self.es.update(index=self.index, doc_type='topics', id=topid,
                       body={"doc": {"must": text}})

    def load_sample_topics(self, topics_json):
        # delete previous index
        self.es.indices.delete(index=self.index, ignore=[400, 404])
        # define mapping
        self.es.indices.create(index=self.index, ignore=400, body={})
        for topic in topics_json:
            description = twokenize(topic['description'], no_duplicates=False)
            narrative = twokenize(topic['narrative'], no_duplicates=False)
            title = twokenize(topic['title'], no_duplicates=False)
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

    def tokenize_in_es(self, text):
        tokens = self.es.indices.analyze(index=self.index, analyzer='english', text=text)
        return [token['token'] for token in tokens['tokens']]

    def load_sample_topics_with_relevance(self, topics_json):
        # delete previous index
        self.es.indices.delete(index=self.index, ignore=[400, 404])
        # define mapping
        self.es.indices.create(index=self.index, ignore=400, body={})
        for topic in topics_json:
            description = twokenize(topic['description'], no_duplicates=False)
            narrative = twokenize(topic['narrative'], no_duplicates=False)
            title = twokenize(topic['title'], no_duplicates=False)
            print title

            relevant = [twokenize(tweet) for tweet in topic['relevant']]
            irrelevant = [twokenize(tweet) for tweet in topic['relevant']]
            # irrelevant_tokens = [token for token in tweet for tweet in relevant if token in ]


            # title_babelfy = babelfy_query(title)
            # print title_babelfy
            self.es.index(index=self.index, doc_type='topics', id=topic['topid'],
                          body={'title': topic["title"].lower(),
                                'title_stem': title,
                                # 'title_babelfy': title_babelfy,
                                'description_stem': description,
                                'narrative_stem': narrative,
                                'description': topic["description"].lower(),
                                'narrative': topic["narrative"].lower(),
                                'relevant': relevant,
                                'irrelevant': irrelevant
                                })


def load_topics_in_ES(file, index_name):
    topics_json = json.load(open(file))
    es = ESClient(index=index_name)
    es.load_sample_topics(topics_json)


def test_search_all():
    es = ESClient(index=INDEX)
    text = "Katy Perry and Taylor Swift feud" #u'_score': 56.553635
    # text = "side effect of the HPV vaccine" # u'_score': 48.15171
    # text = "term limit politicians" #42.087566
    # text = "Im ordering pizza at Panera Bread" #44.941032
    # 29.61396 FP
    # text = '''"luktianashawty justin bieber is my pick for https://t.co/pcjuxjgigc fan army #beliebers https://t.co/tqqa36sxdq"'''
    # text = "justin bieber will have a concert next tuesday" #u'_score': 41.85231
    # text = "cun_taynara rt @justinbie8er94: rt to vote #mtvhottest justin bieber https://t.co/u7v6b5gibz Justin Bieber"
    # 11.242464
    # text = '''uoiae ＠llililill  july 23, 2017 at 06:25amjuly 23, 2017 at 06:25amjuly 23, 2017 at 06:25amjuly 23, 2017 at 06:25amjuly 23, 2017 at 06:25amjuly …'''
    # remove duplicates
    text = ' '.join(set(text.split(' ')))
    # threshold = 40
    # tokens = text.split(" ")
    # clean_text = [token for token in tokens if token not in stoplist]
    # query = twokenize(text)
    results = es.search_all(query=text, explain=True)
    print results
    # topic = results['hits']['hits'][0]
    # title_terms = set(topic['_source']['title_terms'])
    # if title_terms.issubset(set(es.tokenize_in_es(text))):
    #     print topic['_source']['title']


def test_search():
    es = ESClient(index=INDEX)
    text = "feud"
    # query = twokenize(text)
    query = text
    results = es.search_td(query=query, threshold=0, explain=True)
    print results

# def test_search(debug=DEBUG, explain=EXPLAIN):
#     es = ESClient(index='trec17sample')
#     nerrors = 0

#     scores = []
#     for tweet in FALSE:
#         query = twokenize(tweet)
#         if debug:
#             results = es.search_topics(query=query, threshold=0, explain=explain)
#             score = report_results(query, results, es)
#             if score:
#                 scores.append(score)
#         else:
#             results = es.search_topics(query=query)
#             if results:
#                 print 'Query:', query
#                 print 'Topic:', results['_source']['title']

#                 # encorporate negative relevance feedback
#                 title_tokens = results['_source']['title_stem'].split(' ')
#                 description_tokens = results['_source']['description_stem'].split(' ')
#                 relevant_tokens = title_tokens + description_tokens
#                 relevant = ' '.join([token for token in relevant_tokens if token not in query])
#                 if relevant:
#                     print 'Missing evidance:', relevant
#                     # update topic with relevance feedback
#                     es.positive_relevance(topid=results['_id'], text=relevant)

#                 print "Error FP!"
#                 nerrors += 1
#     if scores:
#         print 'Maximium FP score:', max(scores)


#     scores = []
#     for tweet in TRUE:
#         query = twokenize(tweet)
#         if debug:
#             results = es.search_topics(query=query, threshold=0, explain=explain)
#             score = report_results(query, results, es)
#             if score:
#                 scores.append(score)
#         else:
#             results = es.search_topics(query=query)
#             if not results:
#                 print 'Query:', query
#                 print "Error FN!"
#                 nerrors += 1
#             else:
#                 print 'Query:', query
#                 print 'Topic:', results['_source']['title']

#                 # encorporate positive relevance feedback
#                 # relevant = ' '.join([token for token in results['_source']['title_stem'].split(' ') if token in query])
#                 # print 'Relevance evidance:', relevant
#                 # # update topic with relevance feedback
#                 # es.positive_relevance(topid=results['_id'], text=relevant)

#     if scores:
#         print 'Minimum FN score:', min(scores)



#     print '#Errors: ', nerrors


def report_results(tweet, results, es):
    print 'Tweet:', tweet

    if results:
        if EXPLAIN:
            print results
        print 'Topic:', results['_source']['title']
        # print results['_source']['description']
        score = results['_score']
        print score
        return score
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
    tweet1 = 'a on bodyhttps://t.co/ot7mw1gunz show of de GiannaNicolston france photos tour race effects human shocking the cyclist’s'
    tweet2 = 'a on Julia_Harris99 show of de france photos tour race effects human bodyhttps://t.co/zsdilwi8uh shocking the cyclist’s'

    # preprocess tweets
    # tweet1 = twokenize(tweet1)
    # tweet2 = twokenize(tweet2)

    print tweet1
    print tweet2

    es = ESClient(index='trec17')
    # store tweet in ES
    es.store_tweet('test22', tweet1)
    # check duplicates
    duplicates = es.search_tweets(query=tweet2)
    print duplicates
    assert duplicates
    if duplicates:
        print 'Duplicate!'


if __name__ == '__main__':
    # reset: reload topics to ES
    # load_topics_from_file()
    test_duplicate_detection()
