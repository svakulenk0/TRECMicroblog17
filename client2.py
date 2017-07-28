'''
23 July 2017
svakulenko

Twitter stream topic matcher via ElasticSearch expanded with search snippets from Google Custom Search API
'''
import requests
import re

from tweepy.streaming import StreamListener
from tweepy import Stream, API, OAuthHandler

from elasticsearch import Elasticsearch

from settings import *
from sample_tweets import TRUE, FALSE

THRESHOLD = 61

INDEX = 'google'

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
                    "fields": ['description', 'narrative', 'search_snippets']
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
    results = es.search(index=index, body=request, doc_type='topics', explain=explain)['hits']
    # filter out the scores below the specified threshold
    if results['max_score'] > threshold:
        topic = results['hits'][0]
        # topic title terms have to be subset of the tweet
        # title_terms = set(topic['_source']['title_terms'])
        # if title_terms.issubset(set(tokenize_in_es(query, index))):
        return topic
    return None


def test_search_all():
    for tweet in TRUE+FALSE:
        
        # preprocess tweet
        # remove urls
        tweet = re.sub(r"(?:\@|https?\://)\S+", "", tweet)
        tokens = tokenize_in_es(tweet)
        query = ' '.join(f7(tokens))
        print (query)

        # query = "justin bieber will have a concert next tuesday"
        results = search_all(query, threshold=0, explain=True, index=INDEX)
        if results:
            print (results['_score'])
        # print results


def search_duplicate_tweets(query, threshold=13, index=INDEX):
    results = es.search(index=index, body={"query": {"match": {"tweet": query}}}, doc_type='tweets')['hits']
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
        author = status.user.screen_name
        # ignore retweets
        if not hasattr(status,'retweeted_status') and status.in_reply_to_status_id == None:
            text = status.text.replace('\n', '')
            # text = ' '.join([author, text])
            report = text
            # if status.entities[u'user_mentions']:
            #     mentions = ' '.join([entity[u'name'] for entity in status.entities[u'user_mentions']])
            #     report += '\nMentions: ' + mentions
            #     text = ' '.join([text, mentions])
            # if status.entities[u'urls']:
            #     report += '\nURL'
            # if [u'media'] in status.entities.keys():
            #     report += '\nMEDIA'

            # preprocess tweet
            # remove urls
            text = re.sub(r"(?:\@|https?\://)\S+", "", text)
            if text:
                tokens = tokenize_in_es(text)
                if tokens:
                    query = ' '.join(f7(tokens))

                    # query elastic search
                    results = search_all(query=query, threshold=THRESHOLD)
                    if results:
                        # check duplicates
                        duplicates = search_duplicate_tweets(query=query)
                        if not duplicates:
                            # report tweet
                            print ('Tweet:', report)
                            # sent to ES
                            print ('Query:', query)
                            print (results['_score'])
                            title = results['_source']['title']
                            print (title)
                            print (results['_source']['description'])
                            print (results['_source']['narrative'])

                            topid = results['_id']

                            # send push notification
                            # resp = requests.post(API_BASE % ("tweet/%s/%s/%s" %(topid, status.id, CLIENT_IDS[2])))
                            # print resp
                            # assert resp == '<Response [204]>'

                            twitter_client.update_status(title + ' https://twitter.com/%s/status/%s' % (author, status.id))

                            # store tweets that have been reported to ES
                            store_tweet(topid, query)
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
            stream.sample(languages=['en'])
        except Exception as e:
            # reconnect on exceptions
            print (e)
            continue


if __name__ == '__main__':
    # test_search_all()
    stream_tweets()
