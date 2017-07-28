# -*- coding: utf-8 -*-

'''
svakulenko
22 July 2017
'''

import json
import string
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from settings import *
from mappings import *
from topic2wiki import get_wiki_pages
from search_google import search_google
from scrape_duckduckgo import get_relevant_article


es = Elasticsearch()


def tokenize_in_es(text, index_name):
    tokens = es.indices.analyze(index=index_name, analyzer='english', text=text)
    return [token['token'] for token in tokens['tokens']]


def make_documents(f, index_name):
    topics_json = json.load(f)
    for topic in topics_json:

        title = topic['title']
        title_terms = tokenize_in_es(title, index_name)

        doc = {
                '_op_type': 'index',
                '_index': INDEX,
                '_type': 'topics',
                '_id': topic['topid'],
                '_source': {'title': title,
                            'title_terms': title_terms,
                            'description': topic['description'],
                            'narrative': topic['narrative'],
                            }
        }
        yield( doc )


def make_documents_expanded(f, index_name, limit=None, wiki=True, google=True, duckduck=True):
    topics_json = json.load(f)
    if limit:
        topics_json = topics_json[:limit]
    for topic in topics_json:

        topic_title = topic['title']
        print(topic_title)
        title_terms = tokenize_in_es(topic_title, index_name)

        topic_description = topic['description']
        # print topic_description

        doc = {
                '_op_type': 'index',
                '_index': index_name,
                '_type': 'topics',
                '_id': topic['topid'],
                '_source': {'title': topic_title,
                            'title_terms': title_terms,
                            'description': topic_description,
                            'narrative': topic['narrative']
                            }
              }
        if wiki:
            # query expansion with Wikipedia articles
            wiki_result = get_wiki_pages(topic_title)
            if wiki_result:
                wiki_title, wiki_summary, wiki_content = wiki_result
                print (wiki_title)
                doc['_source']['wiki_title'] = wiki_title
                doc['_source']['wiki_summary'] = wiki_summary
                doc['_source']['wiki_content'] = wiki_content

        if google:
            google_result = search_google(topic_description)
            if google_result:
                doc['_source']['search_snippets'] = google_result

        if duckduck:
            duckduck_result = get_relevant_article(topic_description)
            if duckduck_result:
                doc['_source']['web_page'] = duckduck_result

        yield( doc )


# load topics into ES index in bulk
def load_topics_in_ES(index_name, file=TOPICS, document_processor=make_documents):
    # es.indices.delete(index=index_name)
    es.indices.create(index=index_name, body=create_index_body)

    with open(file, "r") as f:
        bulk(es, document_processor(f, index_name))


if __name__ == '__main__':
    load_topics_in_ES(document_processor=make_documents_expanded, index_name='google')
