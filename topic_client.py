from tweepy.streaming import StreamListener
from tweepy import Stream, API, OAuthHandler
import requests
import json
import argparse
from httplib import IncompleteRead # Python 2
# from http.client import IncompleteRead # Python 3

from settings import *
from es_search import ESClient
from tweet_preprocess import twokenize, f7


topics = dict()
topics_matrix = None
twitter_client = None

# set up ES connection
es = ESClient(index=INDEX)

# set up Twitter connection
auth_handler = OAuthHandler(APP_KEY, APP_SECRET)
auth_handler.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter_client = API(auth_handler)


class TopicListener(StreamListener):

    def on_status(self, status):
        author = status.user.screen_name
        # ignore retweets
        if not hasattr(status,'retweeted_status'):
        # if author != MY_NAME:
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
            # query = twokenize(text)
            tokens = es.tokenize_in_es(text)
            query = ' '.join(f7(tokens))
            # query = text
            # query = ' '.join(set(text.split(' ')))

            # query elastic search
            # results = es.search_topics(query=query)
            # results = es.search_titles(query=query, threshold=6)
            # results = es.search_td(query=query, threshold=8, explain=True)
            results = es.search_all(query=query, threshold=19)
            if results:
                # print query
                # check duplicates
                duplicates = es.search_tweets(query=query)
                if not duplicates:
                    # report tweet
                    print 'Tweet:', report
                    # sent to ES
                    print 'Query:', query

                    # print 'Mentions:', mentions
                    print results['_score']
                    title = results['_source']['title']
                    print title
                    print results['_source']['description']
                    print results['_source']['narrative']

                    topid = results['_id']

                    # send push notification
                    # resp = requests.post(API_BASE % ("tweet/%s/%s/%s" %(topid, status.id, CLIENT_IDS[0])))
                    # assert resp == '<Response [204]>'

                    twitter_client.update_status(title + ' https://twitter.com/%s/status/%s' % (author, status.id))
                    # twitter_client.retweet(status.id)

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
    listener = TopicListener()

    # start streaming
    while True:
        try:
            stream = Stream(auth_handler, listener)
            print 'Listening...'
            stream.sample(languages=['en'])
        except Exception as e:
            # reconnect on exceptions
            print e
            continue


def get_topics(clientid=CLIENT_IDS[0], path=TOPICS):
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
