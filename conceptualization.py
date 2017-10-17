# -*- coding: utf-8 -*-
'''
svakulenko
17 july 2017
'''
import requests
import json
import rdflib

# from tweet_preprocess import *
from settings import BABELFY_KEY

# filter out only dbpedia concepts by labels &subject=*dbpedia* 
LOTUS_API = "http://lotus.lodlaundromat.org/retrieve?match=%s&predicate=label&langtag=en&minmatch=100&cutoff=0.005&rank=%s&size=%i&string=%s"
# LODALOT_API = 'http://webscale.cc:3001/LOD-a-lot?%s=%s'
LODALOT_API = 'http://webscale.cc:3001/triple?%s=%s'
# http://webscale.cc:3001/triple?subject=BookMaggie%3A_A_Girl_of_the_Streets
# http://webscale.cc:3001/triple?subject=A-Ha:Top/Arts/Music/Bands_and_Artists/A/A-Ha

BABELFY_API = 'https://babelfy.io/v1/disambiguate'
# TODO tokenization
SAMPLE_TITLES = ["Miss Fisher's Murder Mysteries"]
SAMPLE_CONCEPTS = ['side effects', 'HPV vaccine']


def load_sample_terms():
    # load sample topics
    topics_json = json.load(open('data/sample_topic.json'))
    return topics_json['terms_man']


def babelfy_query(text, lang='EN', match='EXACT_MATCHING', candidates='TOP'):
    params = {
        'text': text,
        'lang': lang,
        'match': match,
        'cands': candidates,
        'posTag': 'NOMINALIZE_ADJECTIVES',
        'key': BABELFY_KEY,
        'dens': 'true'
    }
    resp = requests.post(BABELFY_API, data=params)
    # print resp.json()
    return [hit['DBpediaURL'] for hit in resp.json()]


class SnowBall():
    '''
    Helper class for graph traversal
    '''
    def __init__(self, max_depth=3):
        '''
        max_depth <int> regulates number of nodes to expand termination condition for the graph traversal
        '''
        self.concepts = []
        self.neighbors = []
        self.max_depth = max_depth

    def lotus_recursive_call(self, original, found_texts=[], size=10, filter_ns=False, verbose=False):
        '''
        '''
        # avoid calling the API several times for the same term
        if original not in found_texts:
            # print original
            concepts, found_text = get_concepts_from_lotus(original, size=size, filter_ns=filter_ns)
            
            if found_text:
                if verbose:
                    print (found_text)
                    print (concepts)
                    print ('\n')
                found_texts.append(found_text)
                self.concepts.append(concepts)
                # process the rest of the string
                leftover = original.replace(found_text, "").strip()
            else:
                # skip the 1st word
                leftover = " ".join(original.split(" ")[1:])
            if leftover:
                lotus_recursive_call(leftover, found_texts, filter_ns=filter_ns, verbose=verbose)

    def traverse_graph(self, concept, position, verbose=False):
        # print concept
        # print position
        nns, description = lookup_nns(concept, position)
        # nns, description = lookup_nns(concept, position='object')
        # if description:
        #     descriptions.append(description)
        if nns:
            if verbose:
                print concept
                print position
                print nns
                print '\n'
            # recursion
            self.loop_concept_expansion(nns)
        # return (visited, descriptions)


    def loop_concept_expansion(self, concept_uris, descriptions=[]):
        '''
        finds the immediate neighbourhood 
        '''
        # print len(self.neighbors)
        # print nhops
        # if len(self.neighbors) < self.width:
        for concept in concept_uris:
            if concept not in self.neighbors:
                self.neighbors.append(concept)
                self.traverse_graph(concept, position='subject')
                self.traverse_graph(concept, position='object')
        # return (visited, descriptions)


def get_concepts_from_lotus(text, match='phrase', rank='lengthnorm', size=5, filter_ns=False):
# def get_concepts_from_lotus(text, match='terms', rank='lengthnorm', size=5, filter_ns='dbpedia'):
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
            concepts, text = get_concepts_from_lotus(text, filter_ns=filter_ns)
        
        return concepts, text
    except:
        return None, None


def lookup(concept_uri, position='subject'):
    '''
    check all positions, i.e. explore the graph in both directions
    '''
    # call ldf
    resp = requests.get(LODALOT_API % (position, concept_uri))
    # print resp.content
    if resp.status_code == requests.codes.ok:
        triples = resp.text.split('\n')[2:]
        return triples


def lookup_nns(concept_uri, position='subject'):
    '''
    lookup nearest neighbours in LOD-a-lot
    collect textual descriptions in English as well 
    '''
    nns_rdf = lookup(concept_uri, position)
    if nns_rdf:
        # print nns_rdf

        g = rdflib.Graph()

        for triple in nns_rdf:
            try:
                g.parse(data=triple, format='ntriples')
            except:
                print (triple)

        nns = set()
        descriptions = set()
        for s, p, o in g:
            if type(o) == rdflib.term.URIRef:
                nns.add(str(o.encode('utf-8')))
            # collect English descriptions
            elif type(o) == rdflib.term.Literal and o.language == 'en':
                descriptions.add(str(o))

        return (list(nns), list(descriptions))

    return None, None


def test_babelfy():
    query = 'renewable energy'
    # query = 'stuwerviertel'
    print babelfy_query(query)


def test_lotus():
    query = 'Hawaii Renewable Energy Generation By Resource'
    # query = 'stuwerviertel'
    concepts = lotus_recursive_call(query, filter_ns=False, size=10, verbose=True)


def test_get_concepts():
    # for title in SAMPLE_TITLES:
    #     print get_concepts_from_lotus(title, )

    # terms = load_sample_terms()
    # for term in SAMPLE_CONCEPTS:
    #     print term

    # concepts = babelfy_query("What injuries happened in this year's Tour de France?")

    query = 'New Distributed Renewable Energy Systems Installed in Hawaii'
    concepts = lotus_recursive_call(query, filter_ns=False, size=10, verbose=True)
    if concepts:
        for concept_uris in concepts:
            print (concept_uris)

            # expand concepts
            concepts, descriptions = loop_concept_expansion(concept_uris)
            print (concepts)
            for hop in descriptions:
                for description in hop:
                    print (description)

    # print lookup('http://dbpedia.org/resource/IT_Security')

    # print get_concepts_from_lotus('HPV vaccine side effects')

    # print babelfy_query('Study affirms safety of HPV4 #vaccine for adolescents, young women in routine clinical care: http://bit.ly/U89IAm  #hpv #research')
    # print babelfy_query('#HPV Vaccine Is Safe: The benefits, such as prevention of #cancer, outweigh the risks of possible side effects (PDF) http://bit.ly/2uO5emt ')


if __name__ == '__main__':
    # test_babelfy()
    test_get_concepts()
