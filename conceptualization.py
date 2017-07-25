# -*- coding: utf-8 -*-
'''
svakulenko
17 july 2017
'''
import requests
import json
import rdflib

from tweet_preprocess import *
from settings import BABELFY_KEY

# filter out only dbpedia concepts by labels &subject=*dbpedia*
LOTUS_API = "http://lotus.lodlaundromat.org/retrieve?langtag=en&match=%s&predicate=label&minmatch=100&cutoff=0.005&rank=%s&size=%i&string=%s"
LODALOT_API = 'http://webscale.cc:3001/LOD-a-lot?%s=%s'

BABELFY_API = 'https://babelfy.io/v1/disambiguate'
# TODO tokenization
SAMPLE_TITLES = ["Miss Fisher's Murder Mysteries"]
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


def lotus_recursive_call(original, found_texts=[], found_concepts=[]):
    '''
    '''
    # avoid calling the API several times for the same term
    if original not in found_texts:
        # print original
        concepts, found_text = get_concepts_from_lotus(original, size=2)
        
        if found_text:
            # print found_text
            # print concepts
            found_texts.append(found_text)
            found_concepts.append(concepts)
            # process the rest of the string
            leftover = original.replace(found_text, "").strip()
        else:
            # skip the 1st word
            leftover = " ".join(original.split(" ")[1:])
        if leftover:
            lotus_recursive_call(leftover, found_texts, found_concepts)
        
        if found_concepts:
            return found_concepts
        else:
            return None


def get_concepts_from_lotus(text, found_concepts=[], match='terms', rank='lengthnorm', size=5, filter_ns='dbpedia'):
    '''
    recursive call to the API
    returns a list of concept URIs from LOTUS API
    sample request to LOTUS API: http://lotus.lodlaundromat.org/retrieve?string=monkey
    Params:
    langtag=en&match=conjunct&rank=psf&size=5&
    match: terms, phrase, conjunct, fuzzyconjunct
    rank: lengthnorm, psf, proximity, semrichness, termrichness, recency

    filter_ns - filter on namespace, e.g. 'dbpedia'
    '''
    resp = requests.get(LOTUS_API % (match, rank, size, text))
    # print resp
    try:
        concepts = set([hit['subject'] for hit in resp.json()['hits']])

        # filter concepts in particular namespace
        if filter_ns:
            concepts = [concept for concept in concepts if concept.find(filter_ns) > -1]
        
        # recursive call
        if not concepts:
            tokens = text.split(' ')
            # 1st part remove last word
            text = " ".join(tokens[:-1])
            # print text
            concepts, text = get_concepts_from_lotus(text, found_concepts)
        else:
            found_concepts.append(concepts)
        
        return found_concepts, text
    except:
        return None, None


def lookup(concept_uri, position='subject'):
    # call ldf
    resp = requests.get(LODALOT_API % (position, concept_uri))
    # print resp.content
    triples = resp.text.split('\n')[2:]
    return triples


def lookup_nns(concept_uri, position='subject'):
    '''
    lookup nearest neighbours in LOD-a-lot
    '''
    nns_rdf = lookup(concept_uri, position)
    # print nns_rdf

    g = rdflib.Graph()

    for triple in nns_rdf:
        g.parse(data=triple, format='ntriples')

    nns = set()
    for s, p, o in g:
        if type(o) == rdflib.term.URIRef:
            nns.add(str(o))

    return list(nns)


def test_get_concepts():
    # for title in SAMPLE_TITLES:
    #     print get_concepts_from_lotus(title, )

    # terms = load_sample_terms()
    # for term in SAMPLE_CONCEPTS:
    #     print term

    # concepts = babelfy_query('HPV vaccine side effects')
    # concepts = lotus_recursive_call('IT security')
    # for concept_uri in concepts:
    #     print concept_uri
    #     lookup(concept_uri)

    print lookup('http://dbpedia.org/resource/IT_Security')

    # print get_concepts_from_lotus('HPV vaccine side effects')

    # print babelfy_query('Study affirms safety of HPV4 #vaccine for adolescents, young women in routine clinical care: http://bit.ly/U89IAm  #hpv #research')
    # print babelfy_query('#HPV Vaccine Is Safe: The benefits, such as prevention of #cancer, outweigh the risks of possible side effects (PDF) http://bit.ly/2uO5emt ')


if __name__ == '__main__':
    test_get_concepts()
