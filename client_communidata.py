# -*- coding: utf-8 -*-
'''
7 Aug 2017
svakulenko

Twitter stream topic matcher via ElasticSearch expanded with search snippets from Google Custom Search API
max score threshold
Search Google snippets
'''
import requests
import re

from tweepy.streaming import StreamListener
from tweepy import Stream, API, OAuthHandler, Cursor

from elasticsearch import Elasticsearch

from settings import *
from sample_tweets import TRUE, FALSE
# 4.1
THRESHOLD = 8.1

INDEX = 'communidata'

# set up Twitter connection
auth_handler = OAuthHandler(APP_KEY, APP_SECRET)
auth_handler.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter_client = API(auth_handler)

# set up ES connection
es = Elasticsearch()


multi = {
            "query": {
                "multi_match" : {
                    "type": "most_fields",
                    "fields": ['search_snippets', 'keywords', 'wiki_title', 'wiki_summary', 'wiki_content']
                }
            }
        }


def tokenize_in_es(text, index=INDEX):
    '''
    Produce tokens from text via ES english analyzer
    '''
    tokens = es.indices.analyze(index=index, analyzer='english', text=text)
    return [token['token'] for token in tokens['tokens']]


def search_all(query, threshold=THRESHOLD, explain=False, index=INDEX):
    '''
    Search tweet through topics in ES index
    '''
    # search in all 3 facets of the topic with equal weights,
    request = multi
    request['query']['multi_match']['query'] = query
    results = es.search(index=index, body=request, doc_type='topic', explain=explain)['hits']
    # filter out the scores below the specified threshold
    if results['max_score']:
        if results['max_score'] > threshold:
            topic = results['hits'][0]
            # topic title terms have to be subset of the tweet
            # title_terms = set(topic['_source']['title_terms'])
            # if title_terms.issubset(set(tokenize_in_es(query, index))):
            return topic
    return None


def process_url(url):
    tokens = re.findall(r"[\w']+", url.lower())
    return ' '.join(tokens)


def test_search_Twitter(query='Stuwerviertel'):
    tweets = twitter_client.search(q=query)
    for status in tweets:
        # print status.location
        # print status.time_zone
        if status.place:
            print status.place.country
            print status.place.full_name
        urls = ' '.join([process_url(url['expanded_url']) for url in status.entities['urls']])
        if hasattr(status, 'retweeted_status'):
            urls = ' '.join([process_url(url['expanded_url']) for url in status.retweeted_status.entities['urls']])
        text = status.text
        author = status.user.screen_name
        tweet = ' '.join([author, text, urls])
        results = search_all(tweet, threshold=0, explain=True, index=INDEX)
        if results:
            score = (results['_score'])
            if score < THRESHOLD:
                # print results['_explanation']
                print status
            print tweet
            print score
            print (results['_source']['keywords'])
            print ('\n')


def test_search_all(tweet):
    for tweet in [tweet]:
        
        # preprocess tweet
        # remove urls
        tweet = re.sub(r"(?:\@|https?\://)\S+", "", tweet)
        tokens = tokenize_in_es(tweet)
        query = ' '.join(f7(tokens))

        # query = "justin bieber will have a concert next tuesday"
        results = search_all(query, threshold=0, explain=True, index=INDEX)
        if results:
            print (results['_explanation'])
            
            print (query)
            print (results['_score'])
            print (results['_source']['keywords'])

            print ('\n')
        # print results


def search_duplicate_tweets(query, threshold=13, index=INDEX):
    results = es.search(index=index, body={"query": {"match": {"tweet": query}}}, doc_type='tweets')['hits']
    if results['max_score']:
        if results['max_score'] > threshold:
            return results['hits'][0]
    return None


def store_tweet(topic_id, tweet_text, index=INDEX):
    es.index(index=index, doc_type='tweets', id=topic_id,
             body={'tweet': tweet_text})


def f7(seq):
    '''
    Order sequence to remove duplicates from tweets preserving order
    '''
    if len(seq) > 1:
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]
    else:
        return seq


class TopicListener(StreamListener):
    '''
    Overrides Tweepy class for Twitter Streaming API
    '''

    def on_status(self, status):
        # ignore retweets
        if not hasattr(status,'retweeted_status') and status.in_reply_to_status_id == None:
            print(status.text)
            author = status.user.screen_name
            twitter_client.update_status(' https://twitter.com/%s/status/%s' % (author, status.id))

    def on_status_old(self, status):
        author = status.user.screen_name
        # ignore retweets
        if not hasattr(status,'retweeted_status') and status.in_reply_to_status_id == None:
            text = status.text.replace('\n', '')
            text = ' '.join([author, text])
            report = text
            if status.entities[u'user_mentions']:
                mentions = ' '.join([entity[u'name'] for entity in status.entities[u'user_mentions']])
                report += '\nMentions: ' + mentions
                text = ' '.join([text, mentions])
            if status.entities[u'urls']:
                report += '\nURL'
            if [u'media'] in status.entities.keys():
                report += '\nMEDIA'

            # preprocess tweet
            # remove urls
            text = re.sub(r"(?:\@|https?\://)\S+", "", text)
            if text:
                tokens = tokenize_in_es(text)
                if tokens:
                    # print(tokens)
                    query = ' '.join(f7(tokens))
                    # print(query)
                    # query elastic search
                    results = search_all(query=query, threshold=THRESHOLD)
                    if results:
                        # check duplicates
                        # duplicates = search_duplicate_tweets(query=query)
                        # if not duplicates:

                        # report tweet
                        print ('Tweet:', report)
                        # sent to ES
                        print ('Query:', query)
                        print (results['_score'])
                        topic = results['_source']['keywords']
                        print (topic)


                        # twitter_client.update_status(topic + ' https://twitter.com/%s/status/%s' % (author, status.id))
                        
                        # store tweets that have been reported to ES
                        # topid = results['_id']
                        # store_tweet(topid, query)
                        
                        print ('\n')

        return True

    def on_error(self, status_code):
      print (status_code, 'error code')


def stream_tweets():
    '''
    Connect to Twitter API and fetch relevant tweets from the stream
    '''
    listener = TopicListener()

    # start streaming
    while True:
        try:
            stream = Stream(auth_handler, listener)
            print ('Listening...')
            # stream.sample(languages=['de'])
            stream.filter(track=['stuwerviertel'])
        except Exception as e:
            # reconnect on exceptions
            print (e)
            continue


if __name__ == '__main__':
    # test_search_all('Habe eben „Thirteen Days“ über die Kubakrise angeschaut. Beruhigend, dass wir mit #Trump doch weiter entfernt von WW3 sind, als damals.')
    # test_search_Twitter(query='stuwerviertel')
    stream_tweets()
