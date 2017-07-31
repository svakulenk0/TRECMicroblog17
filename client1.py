'''
23 July 2017
svakulenko

Twitter stream topic matcher via ElasticSearch expanded with a Wikipedia page
max score threshold + title terms subset match
Smarty Wiki
'''
import re

from sample_tweets import TRUE, FALSE
from client import TopicListener
from tweet_preprocess import f7
from settings import *

# 85
THRESHOLD = 36

# INDEX = 'client1'
INDEX = 'client2'


WIKI = {
            "query": {
                "multi_match" : {
                    "type": "most_fields",
                    "fields": ['description', 'narrative', 'wiki_title', 'wiki_summary', 'wiki_content']
                }
            }
        }


def test_search_all():
    listener = TopicListener()
    listener.set_up(threshold=0, index_name=INDEX, request=WIKI, filter_subset=True)

    for tweet in TRUE+FALSE:
        
        # preprocess tweet
        # remove urls
        tweet = re.sub(r"(?:\@|https?\://)\S+", "", tweet)
        tokens = listener.tokenize_in_es(tweet)
        query = ' '.join(f7(tokens))
        print (query)

        # query = "justin bieber will have a concert next tuesday"
        results = listener.search_all(query, explain=True)
        if results:
            print (results['_score'])
        # print results


def stream_tweets():
    '''
    Connect to Twitter API and fetch relevant tweets from the stream
    '''
    listener = TopicListener()
    listener.set_up(threshold=0, index_name=INDEX, request=WIKI, filter_subset=True)
    listener.start_streaming()


if __name__ == '__main__':
    # test_search_all()
    stream_tweets()
