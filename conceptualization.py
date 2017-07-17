# -*- coding: utf-8 -*-
'''
svakulenko
17 july 2017
'''
import requests

from tweet_preprocess import *


LOTUS_API = "http://lotus.lodlaundromat.org/retrieve?string=%s"


def get_concepts(text):
    '''
    returns a list of concept URIs from LOTUS API
    sample request to LOTUS API: http://lotus.lodlaundromat.org/retrieve?string=monkey
    '''
    resp = requests.get(LOTUS_API % text)
    # print resp.json()
    concepts = [hit['subject'] for hit in resp.json()['hits']]
    return concepts


def test_get_concepts():
    print get_concepts('HPV vaccine')


if __name__ == '__main__':
    test_get_concepts()
