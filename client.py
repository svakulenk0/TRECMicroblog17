'''
31 July 2017
svakulenko

TopicsClient class for Twitter
'''
from datetime import datetime
import requests
import re

from tweepy.streaming import StreamListener
from tweepy import Stream, API, OAuthHandler

from elasticsearch import Elasticsearch

from settings import *
from tweet_preprocess import f7


class TopicListener(StreamListener):
    '''
    Overrides Tweepy class for Twitter Streaming API
    '''

    def set_up(self, threshold, index_name, request, filter_subset):
        # similarity threshold
        self.threshold = threshold

        self.index = index_name
        self.request = request
        self.filter_subset = filter_subset

        # set up Twitter connection
        self.auth_handler = OAuthHandler(APP_KEY, APP_SECRET)
        self.auth_handler.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        self.twitter_client = API(self.auth_handler)

        # set up ES connection
        self.es = Elasticsearch()

        # topics skip list due to rate limiting
        self.topics_exceeded = []

        # rate limit per day reset tracker
        self.today = datetime.utcnow().date()

    def on_status(self, status):

        # check UTC for topic skip list restart
        date = datetime.utcnow().date()
        # new day
        if date != self.today:
            # reset topics fresh
            self.topics_exceeded = []
            # and continue tracking time
            self.today = date

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
            tokens = self.tokenize_in_es(text)
            query = ' '.join(f7(tokens))

            # query elastic search
            results = self.search_all(query=query)
            if results:
                # check duplicates
                duplicates = self.search_duplicate_tweets(query=query)
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

                    # respect rate limiting
                    if topid not in self.topics_exceeded:
                        try:
                            # send push notification
                            resp = requests.post(API_BASE % ("tweet/%s/%s/%s" %(topid, status.id, CLIENT_IDS[1])))
                            print (resp)
                            if (resp.status_code == 429):
                                # add topic to the skip list
                                self.topics_exceeded.append(topid)
                                print ("Rate limit exceeded. Topic is added to the ignore list.")
                            else:
                                # store tweets that have been reported to ES
                                self.store_tweet(topid, query)
                        except:
                            print ("Could not push to TREC server")
                    else:
                        print ("Rate limit exceeded. Tweet is skipped.") 

                    # assert resp == '<Response [204]>'

                    self.twitter_client.update_status(title + ' https://twitter.com/%s/status/%s' % (author, status.id))

                    print ('\n')

        return True

    def on_error(self, status_code):
      print (status_code, 'error code')

    def tokenize_in_es(self, text):
        '''
        Produce tokens from text via ES english analyzer
        '''
        tokens = self.es.indices.analyze(index=self.index, analyzer='english', text=text)
        return [token['token'] for token in tokens['tokens']]

    def search_all(self, query, explain=False):
        '''
        Search tweet through topics in ES index
        '''
        # search in all 3 facets of the topic with equal weights,
        self.request['query']['multi_match']['query'] = query
        results = self.es.search(index=self.index, body=self.request, doc_type='topics', explain=explain)['hits']
        # filter out the scores below the specified threshold
        if results['max_score'] > self.threshold:
            topic = results['hits'][0]
            if self.filter_subset:
                # topic title terms have to be subset of the tweet
                title_terms = set(topic['_source']['title_terms'])
                if title_terms.issubset(set(self.tokenize_in_es(query))):
                    return topic
            else:
                return topic
        return None

    def search_duplicate_tweets(self, query, threshold=13):
        results = self.es.search(index=self.index, body={"query": {"match": {"tweet": query}}}, doc_type='tweets')['hits']
        if results['max_score'] > threshold:
            return results['hits'][0]
        return None

    def store_tweet(self, topic_id, tweet_text):
        self.es.index(index=self.index, doc_type='tweets', id=topic_id,
                 body={'tweet': tweet_text})

    def start_streaming(self):
        # start streaming
        while True:
            try:
                stream = Stream(self.auth_handler, self)
                print ('Listening...')
                stream.sample(languages=['en'])
            except Exception as e:
                # reconnect on exceptions
                print (e)
                continue
