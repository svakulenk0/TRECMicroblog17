from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import requests
import json
import argparse
from httplib import IncompleteRead # Python 2
# from http.client import IncompleteRead # Python 3

from settings import *
from es_search import ESClient
from tweet_preprocess import twokenize


topics = dict()
topics_matrix = None

# set up ES connection
es = ESClient(index='trec17')


class TopicListener(StreamListener):

    def on_status(self, status):
        # ignore retweets
        if not hasattr(status,'retweeted_status'):
            text = status.text.lower().replace('\n', '')
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
            query = twokenize(text)
            
            # query elastic search
            results = es.search_topics(query=query)
            if results:

                # check duplicates
                duplicates = es.search_tweets(query=query)
                if not duplicates:

                    # report tweet
                    print 'Tweet:', report
                    # print 'Mentions:', mentions
                    print results['_score']
                    print results['_source']['title']
                    print results['_source']['description']
                    print results['_source']['narrative']

                    topid = results['_id']
                    # send push notification
                    resp = requests.post(API_BASE % ("tweet/%s/%s/%s" %(topid, status.id, CLIENT_IDS[0])))
                    # print resp TODO 204 correct?

                    # store tweets that have been reported to ES
                    es.store_tweet(topid, query)
                    print '\n'

            return True

    def on_error(self, status_code):
      print status_code, 'error code'


def load_sample_topics():
    # use topics from the local dump
    topics_json = json.load(open('data/TREC2017-RTS-topics1.json'))
    for topic in topics_json:
        topics[topic["topid"]] = {'title': topic["title"].lower(),
                                  'description': topic["description"].lower(),
                                  'narrative': topic["narrative"].lower()
                                  }
    # print topics.values()
    print len(topics.keys()), 'topics'
    return topics


def register_clients(n=3):
    '''
    Group can register only a limited number of clients.
    Make sure to store the client id!!!
    '''
    for run in xrange(n):
        response = requests.post(API_BASE % ("register/system"), data = {"groupid": GROUPID, "alias":"WuWien-Run"+str(run+1)}).json()
        if "clientid" in response.keys():
            print response["clientid"]
        else:
            print response


def stream_tweets():
    # set up Twitter connection
    listener = TopicListener()
    auth = OAuthHandler(APP_KEY, APP_SECRET)
    auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    # start streaming
    while True:
        try:
            stream = Stream(auth, listener)
            print 'Listening...'
            stream.sample(languages=['en'])
        except Exception as e:
            # reconnect on exceptions
            # print e
            continue


def get_topics(clientid=CLIENT_IDS[0], path=SAMPLE_TOPICS[1]):
    resp = requests.get(API_BASE % ("topics/%s" % clientid))
    with open(path, 'w') as outfile:
        json.dump(resp.json(), outfile)
        # print resp.json()
    # json.loads(resp.json())
    # for row in resp.json():
        # topics[row["topid"]] = row["query"].lower()


def fetch_feedback(topid='RTS102', clientid=CLIENT_IDS[0]):
    resp = requests.get(API_BASE % ("assessments/%s/%s" % (topid, clientid)))
    print resp
    # TODO ?


if __name__ == '__main__':
    stream_tweets()
    # fetch_feedback()
