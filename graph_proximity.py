# -*- coding: utf-8 -*-
'''
svakulenko
24 july 2017
'''

from conceptualization import get_concepts_from_lotus, lookup, lotus_recursive_call
from process_tweets import tweet_lookup, loop_concept_expansion


TOPIC = {
           "narrative" : "@SwiftOnSecurity is a great twitter account about IT security that targets a broad audience. Tweets from the similar accounts on the IT security topic are also relevant.",
           "title" : "IT security",
           "topid" : "RTS219",
           "description" : "News and reflections about IT security."
        }

SAMPLE_CONCEPT = 'malware'

TRUE = [
        "Just to spell this out: The logging capabilities in PowerShell are so incredibly empowering to defenders that attackers getting worried.",
        "If you're configuring your corporate antivirus to send no threat data and only get updates from your AV server, you're far more vulnerable.",
        '''Approximately 96% of all [malware hashes] detected and blocked by Windows Defender Antivirus (Windows Defender AV) are observed only once'''
        ]
FALSE = [
         "Security Cams - Best Source for Security Cameras, Surveillance Systems and Security DVRs http://ref.gl/kbxCwBQj ",
         "ಇಂಡಿಯನ್ politicians n border security force also have their good share...",
         '''••Great Full Time Benefits at General Security Services Corporation!•• http://JobGuideND.com''',
        ]


def find_path(topic, tweet):
    # link topic
    concept, text = get_concepts_from_lotus(topic)
    concept_uri = list(concept)[0]
    print concept_uri

    # tweet_concepts = tweet_lookup(topic)
    # for token in tweet_concepts:
    #     print (token)
    #     loop_concept_expansion(token, nhops=13)

    # concepts = lotus_recursive_call(topic, filter_ns=False, size=10, verbose=True)
    # if concepts:
    #     for concept_uris in concepts:
    #         print (concept_uris)

    # link tweet
    # concept, text = get_concepts_from_lotus(tweet)
    # print concept
    # concept_uri = list(concept)[0]
    # print concept_uri
    tweet_concepts = tweet_lookup(tweet)
    for token in tweet_concepts:
        print (token)
        loop_concept_expansion(token, nhops=2)
    # concept_uri = list(concept)[0]
    # print concept_uri
    # print lookup(concept_uri)


def test_find_path():
    '''
    Make sure we can find the path between "IT security" and "malware"
    e.g.
    https://en.wikipedia.org/wiki/Computer_security
    linksTo
    https://en.wikipedia.org/wiki/Information_security
    linksTo
    https://en.wikipedia.org/wiki/Malware
    '''
    topic = TOPIC['title']
    tweet = SAMPLE_CONCEPT
    find_path(topic, tweet)


def main():
    test_find_path()


if __name__ == '__main__':
    main()
