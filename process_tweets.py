# -*- coding: utf-8 -*-
'''
svakulenko
24 july 2017
'''

import re

from conceptualization import get_concepts_from_lotus
from tweet_preprocess import twokenize, MYSTOPLIST


# sample tweets
true = "logging PowerShell defenders attackers"
false = "Security Cameras Surveillance Systems"
# real = "Someone give me 2 tickets to the justin bieber concert in Arlington,Tx so me and my mom can go"
real = "The Iris Tank One Piece Swimsuit is a classic statement one piece, perfect for every beach girl. The features of... http://fb.me/1wXYqZnKy"


def lotus_recursive_call(original, found=None):
    '''
    '''
    concepts, found = get_concepts_from_lotus(original)
    print found
    print concepts
    
    if concepts:
        leftover = original.replace(found,"").strip()
        if leftover:
            lotus_recursive_call(leftover, found)


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

    # lowercase to detect all stopwords
    text = text.lower()

    # split string into segments on punctuation
    segments = re.split(r'[,;.-]+\s', text)

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


def test_tokenize(tweet=real, tokenize=segment_on_stopwords):
    print tweet
    print tokenize(tweet)


def test_process_string(tweets=[true, false]):
    # iterate over tweets
    for tweet in tweets:
        print tweet
        print '\n'
        lotus_recursive_call(tweet)
        print '\n'


def test_process_tokens(tweets=[real], tokenize=segment_on_stopwords):
    # iterate over tweets
    for tweet in tweets:
        print tweet
        tokens = tokenize(tweet)
        print tokens
        print '\n'
        for token in tokens:
            lotus_recursive_call(token)
        print '\n'


if __name__ == '__main__':
    test_tokenize()
    # test_process_string()