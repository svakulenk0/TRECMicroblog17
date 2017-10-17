# -*- coding: utf-8 -*-
'''
svakulenko
24 july 2017
'''

import re

from conceptualization import lookup_nns
from tweet_preprocess import twokenize, MYSTOPLIST
from sample_tweets import TRUE, FALSE


# sample tweets
true = "logging PowerShell defenders attackers"
false = "Security Cameras and Surveillance Systems"
sample = "Im ordering pizza at Panera Bread"
real = "••Great Full Time Benefits at General Security Services Corporation!•• http://JobGuideND.com "

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


def close_segment(current_segment, segments):
    if current_segment:
        # add current_segment to segments
        segments.append(current_segment)
        current_segment = None
    return current_segment, segments


def segment_on_stopwords(text, stopwords=MYSTOPLIST):
    '''
    spilts string on stopwords
    '''

    # remove urls
    text = re.sub(r"(?:\@|https?\://)\S+", " ", text)

    # remove unicode characters
    text = re.sub(r'[^\x00-\x7F]+',' ', text)

    # remove symbols #
    text = re.sub(r"(#)", "", text)

    # lowercase to detect all stopwords
    text = text.lower()

    # split string into segments on punctuation
    segments = re.split(r'[,;:.()!?\[\]-]', text)

    # split segments into word tokens to detect stopwords
    segments = [segment.split() for segment in segments]

    new_segments = []
    current_segment = None

    for segment in segments:
        for token in segment:
            # print current_segment
            if token in stopwords:
                current_segment, new_segments = close_segment(current_segment, new_segments)
            else:
                # continue accumulating current_segment
                if current_segment:
                    current_segment = ' '.join([current_segment, token])
                else:
                    current_segment = token
        current_segment, new_segments = close_segment(current_segment, new_segments)
    current_segment, new_segments = close_segment(current_segment, new_segments)

    return new_segments


def test_tokenize(tweet=TRUE[0], tokenize=segment_on_stopwords):
    print (tweet)
    # print tokenize(tweet)


def test_process_string(tweets=[true, false]):
    # iterate over tweets
    for tweet in tweets:
        # print tweet
        # print '\n'
        lotus_recursive_call(tweet)
        # print '\n'


def test_process_tokens(tweets=TRUE+FALSE, tokenize=segment_on_stopwords):
    # iterate over tweets
    for tweet in tweets:
        print (tweet)
        tokens = tokenize(tweet)
        # print tokens
        # print '\n'
        for token in tokens:
            lotus_recursive_call(token, verbose=True)
        # print '\n'


def tweet_lookup(tweet, tokenize=segment_on_stopwords):
    print (tweet)
    tokens = tokenize(tweet)
    print (tokens)

    concepts = []

    for token in tokens:
        # print token
        token_concepts = lotus_recursive_call(token, [], [])
    # return token_concepts
        concepts.append(token_concepts)

    return concepts


def test_tweet_lookup(tweets=[true], tokenize=segment_on_stopwords):
    for tweet in tweets:
        tweet_concepts = tweet_lookup(tweet, tokenize)
        print (tweet_concepts)
        # print '\n'


def test_tweet_concept_expansion(tweet=true):
    tweet_concepts = tweet_lookup(tweet)
    for token in tweet_concepts:
        
        # 1s hop
        for alternative in token:
            nns = lookup_nns(alternative)
            if nns:
                # print alternative
                # print nns
                
                # 2nd hop
                for alternative in nns:
                    nns = lookup_nns(alternative)
                    if nns:
                        print (alternative)
                        # print nns


def test_loop_tweet_concept_expansion(tweets=[true]):
    for tweet in tweets:
        # print tweet
        tweet_concepts = tweet_lookup(tweet)
        for token in tweet_concepts:
            print (token)
            loop_concept_expansion(token, nhops=2)


if __name__ == '__main__':
    # test_tokenize()
    # test_process_string()
    # test_process_tokens()
    # test_tweet_lookup()
    test_loop_tweet_concept_expansion()
