# -*- coding: utf-8 -*-
'''
svakulenko
7 Aug 2017
'''
from elasticsearch import Elasticsearch

from conceptualization import lotus_recursive_call, loop_concept_expansion
from topic2wiki import get_wiki_pages
from search_google import search_google
from scrape_duckduckgo import get_relevant_article


# do not track similar keywords since it will increase IDF
# SEEDS = ['Österreich', 'Wien', 'Leopoldstadt', 'Stuwerviertel']

# provide alternative keywords
# add random, also neutral completely unrelated, keywords but which have wiki pages in the language of interest to reduce the contribution from stopwords
SEEDS = ['Stuwerviertel', 'Kreuzberg', 'Wiedikon']


mapping = {
      'settings': {
        # just one shard, no replicas for testing
        'number_of_shards': 1,
        'number_of_replicas': 0,
      },
      'mappings': {
        'topics': {
          'properties': {
            'keywords': {'type': 'text', 'analyzer': 'german'},
            # 'keywords': {'type': 'text', 'analyzer': 'standard'},
            'search_snippets': {'type': 'text', 'analyzer': 'german'},
            'wiki_title': {'type': 'text', 'analyzer': 'german'},
            'wiki_summary': {'type': 'text', 'analyzer': 'german'},
            'wiki_content': {'type': 'text', 'analyzer': 'german'},
            # 'search_snippets': {'type': 'text', 'analyzer': 'standard'},
          }
        },
        'tweets': {
          'properties': {
            'tweet': {'type': 'text', 'analyzer': 'german'},
            # 'tweet': {'type': 'text', 'analyzer': 'standard'},
          }
        }
      }
    }

def get_LODaLot(keywords='Leopoldstadt'):
    concepts = lotus_recursive_call(keywords, filter_ns=False, size=10)
    if concepts:
        for concept_uris in concepts:
            print (concept_uris)
            concepts, descriptions = loop_concept_expansion(concept_uris)
            print (concepts)
            for hop in descriptions:
                for description in hop:
                    print (description)


def get_wiki(keywords='Leopoldstadt'):
    wiki = get_wiki_pages(keywords, lang='de')
    if wiki:
        print (wiki[2])


def get_google_snippets(keywords='Stuwerviertel'):
    print (search_google(keywords))


def load_topics_in_ES(topics, index_name='communidata', wiki=True, google=True, duckduck=False):
    es = Elasticsearch()

    # reset index
    try:
        es.indices.delete(index=index_name)
        es.indices.create(index=index_name, body=mapping)
    except Exception as e:
        print (e)

    for i, topic in enumerate(topics):

        doc = {'keywords': topic}

        if wiki:
            # query expansion with Wikipedia articles
            wiki_result = get_wiki_pages(topic, lang='de')
            if wiki_result:
                wiki_title, wiki_summary, wiki_content = wiki_result
                print (wiki_summary)
                doc['wiki_title'] = wiki_title
                doc['wiki_summary'] = wiki_summary
                doc['wiki_content'] = wiki_content

        if google:
            google_result = search_google(topic)
            if google_result:
                doc['search_snippets'] = google_result

        if duckduck:
            duckduck_result = get_relevant_article(topic)
            if duckduck_result:
                doc['web_page'] = duckduck_result

        es.index(index=index_name, doc_type='topic', id=i,
                 body=doc)


if __name__ == '__main__':
    load_topics_in_ES(SEEDS)
