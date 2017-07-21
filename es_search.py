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
# from queries import multi_weighted

# stemmed queries after preprocessing tweets
FALSE = [
            '''wand hes show long fact need world joze cole hate best''',
            '''noida lead provid cheap india websit design respons compani best''',
            '''s''',
            '''congressman krishnamoorthi calls on white house counsel to publicly disclose all pardons issued by president trumphttps://t.co/rtgvko9lyd''',
            # '''jazeera al peopl english daylight sad innoc kill broad news''',
            '''trump repealrunan peopl ryan duti mcconnel abdic health want presid senat paul republican sabotag leader care''',
            '''heather show opera day live democraci soap shit''',
            '''wheel c bicycl tire superd cycl aliexpress bike tyre road''',
            '''bill ted say cruz health pass close senat care''',
            '''politician run that cpas profession reason governor businesspeopl offic small amp''',
            '''brexit replac pro worker say british britain cant great remain citizen eu post mock''',
            '''puppi old psa dog matter consid''',
            '''thank standstrong susan commentari bill collin uspolit kill sen health republican senat care women''',
            '''cranston bryan notaaron show ruin itnevr actor side wher amp paul charact think bettr''',
            '''album ankur fre song tyagi ts music snake shadi come fact shook''',
            '''great good woman make thing doesnt take man''',
            '''korea north world rao visit honest bbc santosh moral consid respons news''',
            # '''dizoard mountain le franc rider tour col conquer var final stage''',
            '''plate menu review swindian hey know interest editori small''',
            '''info mueller privat trump year tax lawyer deliv go amp public staff'''
        ]

# real tweets without preprocessing
TRUE = [
            '''The best beach in the world is in Australia near the coral reef''',
            '''i am ordering sweet roll at panera bread''',
            '''we just ordered pizza at panera bread''',
            # '''@bklynborn1971 @mambodave @presssec @jguerrein @potus @realdonaldtrump 😂 huckabee will be next, she better call her daddy for a job.''',
            '''"the rise of sarah huckabee sanders, the new star of the trump administration who's now a contender for spicer's job" by eliza relman via f…''',
            '''justin bieber grabs selena gomez’s butt on way to christmas rehearsals for washington concert (pictures) https://t.co/mq6qwgm6hh''',
            '''the big bang theory's mayim bialik still gets hilariously small checks from ... #buzz #entertainment #news #news https://t.co/sebepyszya''',
            '''taylor swift and zayn malik in sexy new fifty shades music video  https://t.co/8gibyiwqpi''',
            '''isis command helped philippine militants seize marawi through funding &amp; recruits – report — rt news https://t.co/oi3tyakh1i'''
       ]

TOPIC_SIM_THRESHOLD = 37
# weights for title, description, narrative stemmed fields
# last weight is for the must value
BOOSTS = [3, 2, 1, 4]

DEBUG = True
EXPLAIN = False

multi_weighted = {
                    "query": {
                        "multi_match" : {
                            "type": "most_fields",
                            "fields": ["must^%s" % BOOSTS[-1], "title_stem^%s" % BOOSTS[0], 'description_stem^%s' % BOOSTS[1], 'narrative_stem^%s' % BOOSTS[2]]
                        }
                    }
                 }



class ESClient():

    def __init__(self, index):
        self.es = Elasticsearch()
        self.index = index

    def count(self, query, threshold=10):
        return self.es.count(index=self.index, q=query, min_score=threshold)

    def search_tweets(self, query, threshold=10):
        results = self.es.search(index=self.index, q=query, doc_type='tweets')['hits']
        if results['max_score'] > threshold:
            return results['hits'][0]
        return None

    def search_topics(self, query, threshold=TOPIC_SIM_THRESHOLD, explain=False):
        # print query
        request = multi_weighted
        request['query']['multi_match']['query'] = query
        # results = self.es.search(index=self.index, q=query, doc_type='topics')['hits']
        results = self.es.search(index=self.index, body=request, doc_type='topics', explain=explain, size=1)['hits']
        if results['max_score'] > threshold:
            topic = results['hits'][0]
            # if DEBUG:
            #     if 'must' in topic['_source'].keys():
            #         print topic['_source']['must']
            #     return topic
            # else:
            # check that the must terms are in the tweet
            if 'must' in topic['_source'].keys():
                title = set(topic['_source']['must'].split(' '))
                if title.issubset(set(query.split(' '))):
                    return topic
            else:
                return topic
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


def test_search(debug=DEBUG, explain=EXPLAIN):
    es = ESClient(index='trec17sample')
    nerrors = 0

    scores = []
    for query in FALSE:
    # for tweet in SAMPLE_TWEETS:
        # tweet = twokenize(tweet)
        if debug:
            results = es.search_topics(query=query, threshold=0, explain=explain)
            score = report_results(query, results, es)
            if score:
                scores.append(score)
        else:
            results = es.search_topics(query=query)
            if results:
                print 'Query:', query
                print 'Topic:', results['_source']['title']

                # encorporate negative relevance feedback
                relevant = ' '.join([token for token in results['_source']['title_stem'].split(' ') if token not in query])
                if relevant:
                    print 'Missing evidance:', relevant
                    # update topic with relevance feedback
                    es.positive_relevance(topid=results['_id'], text=relevant)

                print "Error FP!"
                nerrors += 1
    if scores:
        print 'Maximium FP score:', max(scores)


    scores = []
    for tweet in TRUE:
        query = twokenize(tweet)
        if debug:
            results = es.search_topics(query=query, threshold=0, explain=explain)
            score = report_results(query, results, es)
            if score:
                scores.append(score)
        else:
            results = es.search_topics(query=query)
            if not results:
                print 'Query:', query
                print "Error FN!"
                nerrors += 1
            else:
                print 'Query:', query
                print 'Topic:', results['_source']['title']
                # encorporate positive relevance feedback
                relevant = ' '.join([token for token in results['_source']['title_stem'].split(' ') if token in query])
                print 'Relevance evidance:', relevant
                # update topic with relevance feedback
                es.positive_relevance(topid=results['_id'], text=relevant)

    if scores:
        print 'Minimum FN score:', min(scores)



    print '#Errors: ', nerrors


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
    tweet1 = 'omg that is not related'
    tweet2 = 'omg that is not related'

    # preprocess tweets
    tweet1 = twokenize(tweet1)
    tweet2 = twokenize(tweet2)

    print tweet1
    print tweet2

    es = ESClient(index='trec17sample')
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
    load_topics_from_file()

    # test_search(debug=False)
