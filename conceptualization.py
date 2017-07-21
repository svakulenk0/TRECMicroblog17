# -*- coding: utf-8 -*-
'''
svakulenko
17 july 2017
'''
import requests
import json

from tweet_preprocess import *
from settings import BABELFY_KEY


LOTUS_API = "http://lotus.lodlaundromat.org/retrieve?langtag=en&match=terms&rank=lengthnorm&size=20&string=%s"
LODALOT_API = 'http://webscale.cc:3001/LOD-a-lot?subject=%s'

BABELFY_API = 'https://babelfy.io/v1/disambiguate'
# TODO tokenization
SAMPLE_CONCEPTS = ['side effects', 'HPV vaccine']


def load_sample_terms():
    # load sample topics
    topics_json = json.load(open('data/sample_topic.json'))
    return topics_json['terms_man']


def babelfy_query(text, lang='EN', match='EXACT_MATCHING', candidates='TOP'):
    service_url = 'https://babelfy.io/v1/disambiguate'
    params = {
        'text': text,
        'lang': lang,
        'match': match,
        'cands': candidates,
        'posTag': 'NOMINALIZE_ADJECTIVES',
        'key': BABELFY_KEY,
        'dens': 'true'
    }
    resp = requests.post(service_url, data=params)
    print resp.json()
    return [hit['DBpediaURL'] for hit in resp.json()]


def get_concepts_from_lotus(text):
    '''
    returns a list of concept URIs from LOTUS API
    sample request to LOTUS API: http://lotus.lodlaundromat.org/retrieve?string=monkey
    '''
    resp = requests.get(LOTUS_API % text)
    print resp.json()
    concepts = set([hit['subject'] for hit in resp.json()['hits']])
    return concepts


def lookup(concept_uri):
    # call ldf
    resp = requests.get(LODALOT_API % concept_uri)
    print resp.text


def test_get_concepts():
    # terms = load_sample_terms()
    # for term in SAMPLE_CONCEPTS:
    #     print term
    concepts = babelfy_query('HPV vaccine side effects')
    for concept_uri in concepts:
        print lookup(concept_uri)
    # print get_concepts_from_lotus('HPV vaccine side effects')

    # print babelfy_query('Study affirms safety of HPV4 #vaccine for adolescents, young women in routine clinical care: http://bit.ly/U89IAm  #hpv #research')
    # print get_concepts_from_lotus('HPV4 #vaccine')
    # print babelfy_query('#HPV Vaccine Is Safe: The benefits, such as prevention of #cancer, outweigh the risks of possible side effects (PDF) http://bit.ly/2uO5emt ')


if __name__ == '__main__':
    test_get_concepts()
