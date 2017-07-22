'''
21 july 2017
svakulenko
'''

from tweepy import API, OAuthHandler

from settings import *


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
    clean_up_my_timeline()