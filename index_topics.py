# -*- coding: utf-8 -*-

'''
svakulenko
22 July 2017
'''

import json
import string
from elasticsearch import Elasticsearch

from settings import *
from mappings import *


class ESClient():
    def __init__(self, index):
        self.es = Elasticsearch()
        self.index = index

    def load_topics(self, topics_json):
        # delete previous index
        self.es.indices.delete(index=self.index, ignore=[400, 404])
        # define mapping
        self.es.indices.create(index=self.index, body=create_index_body)

        for topic in topics_json:
            title = topic['title']

            description = topic['description']

            # table = {ord(char): None for char in string.punctuation}
            # description_clean = description.translate(table)
            
            # description = description.translate(None, string.punctuation)

            narrative = topic['narrative']
            # narrative_clean = narrative.translate(table)


            # td = ' '.join([title, description, narrative])

            # print td


            # relevant, irrelevant = [], []
            # if 'relevant' in topic.keys():
            #     relevant = [twokenize(tweet) for tweet in topic['relevant']]
            # if 'irrelevant' in topic.keys():
            #     irrelevant = [twokenize(tweet) for tweet in topic['irrelevant']]

            # # title_babelfy = babelfy_query(title)
            # # print title_babelfy
            self.es.index(index=self.index, doc_type='topics', id=topic['topid'],
                          body={'title': title,
            #                     'title_stem': title,
            #                     # 'title_babelfy': title_babelfy,
            #                     'description_stem': description,
            #                     'narrative_stem': narrative,
                                # 'td': td,
                                'description': description,
                                'narrative': narrative,
            #                     'relevant': relevant,
            #                     'irrelevant': irrelevant
                                })


# load topics into ES index
def load_topics_in_ES(file=TOPICS, index_name=INDEX):
    topics_json = json.load(open(file))
    es = ESClient(index=index_name)
    es.load_topics(topics_json)


if __name__ == '__main__':
    load_topics_in_ES()
