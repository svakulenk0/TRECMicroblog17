from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import requests
import json
import argparse

from twitter_settings import *
from es_search import ESClient

hostname = ""
port = ""
clientid = ""

topics = dict()
topics_matrix = None


es = ESClient(index='trec17sample')

class TopicListener(StreamListener):

    def on_status(self, status):
        # ignore retweets
        if not hasattr(status,'retweeted_status'):
            text = status.text.lower().replace('\n', '')

            # Simple iterator and exact match
            # for topid, query in topics.items():
            #     # match query to text
            #     if text.find(query['title']) >= 0:
            #         print query
            #         print text

            # query elastic search
            # results = es.search(query=text)['hits']['hits']

            results = es.search_titles(query=text)
            # print len(results)
            if results['hits']:
                print text
                print results

                    # resp = requests.post(api_base % ("tweet/%s/%s/%s" %(topid,status.id,clientid)))
                    # print resp.status_code
            # print '\n'
        return True

    def on_error(self, status_code):
      print status_code, 'error code'


def load_sample_topics():
    # load sample topics
    topics_json = json.load(open('data/TREC2017-RTS-topics1.json'))
    for topic in topics_json:
        topics[topic["topid"]] = {'title': topic["title"].lower(),
                                  'description': topic["description"].lower(),
                                  'narrative': topic["narrative"].lower()
                                  }
    # print topics.values()
    print len(topics.keys()), 'topics'
    return topics

if __name__ == '__main__':
    # api_base= "http://%s:%s/" % (hostname, port)
    # api_base += "%s"

    # resp = requests.post(api_base % ("register/system"), data = {"groupid": "uwar"})
    # clientid = resp.json()["clientid"]

    # resp = requests.get(api_base % ("topics/%s" % clientid))
    # for row in resp.json():
    #   topics[row["topid"]] = row["query"].lower()

    topics = load_sample_topics()

    listener = TopicListener()
    auth = OAuthHandler(APP_KEY, APP_SECRET)
    auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    stream = Stream(auth,listener)
    stream.sample(languages=['en'])
