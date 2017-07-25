# -*- coding: utf-8 -*-

'''
svakulenko
25 July 2017
'''
import json
import wikipedia

from process_tweets import segment_on_stopwords
from conceptualization import lotus_recursive_call
from settings import *


TOPIC = {
           "narrative" : "@SwiftOnSecurity is a great twitter account about IT security that targets a broad audience. Tweets from the similar accounts on the IT security topic are also relevant.",
           "title" : "IT security",
           "topid" : "RTS219",
           "description" : "News and reflections about IT security."
        }


def get_topic_concepts(topic=TOPIC, tokenize=segment_on_stopwords):
    title = topic['title']
    print title
    
    topic_concepts = lotus_recursive_call(title, filter_ns=False, size=1)
    print topic_concepts


def find_in_wiki(string):
    return wikipedia.search(string)


def test_find_in_wiki(topic=TOPIC):
    title = topic['title']
    print title
    print find_in_wiki(title)[0]


def wiki_preprocess(content):
    return content


def get_wiki_pages(string, maxpages=1):
    wiki_page_titles = find_in_wiki(string)[:maxpages]
    
    for page_title in wiki_page_titles:
        page = wikipedia.page(page_title)

        title = page.title
        summary = page.summary
        content = page.content
        # preprocess wiki content
        return title, summary, content
        # print page.links


def test_get_wiki_pages(file=TOPICS, maxtopics=1):
    # iterate over topics
    with open(file, "r") as f:
        topics_json = json.load(f)
        for topic in topics_json[:maxtopics]:
            
            title = topic['title']
            print title
            wiki = get_wiki_pages(title)
            print wiki


if __name__ == '__main__':
    test_get_wiki_pages()
