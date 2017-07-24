'''
21 july 2017
svakulenko
'''
import json

from tweepy import API, OAuthHandler

from settings import *


def load_titles(file=TOPICS):
    with open(file, "r") as f:
        topics_json = json.load(f)
        return [topic['title'] for topic in topics_json]


def load_topics(file=TOPICS):
    with open(file, "r") as f:
        topics_json = json.load(f)
        for topic in topics_json:
            title = topic['title']
            print title


def clean_up_my_timeline(ntweets=100):
    # set up Twitter connection
    auth_handler = OAuthHandler(APP_KEY, APP_SECRET)
    auth_handler.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    twitter_client = API(auth_handler)

    timeline = twitter_client.user_timeline(count = ntweets)

    print "Found: %d" % (len(timeline))
    print "Removing..."

    # Delete tweets one by one
    for t in timeline:
        twitter_client.destroy_status(t.id)


if __name__ == '__main__':
    load_titles()