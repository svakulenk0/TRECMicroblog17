# -*- coding: utf-8 -*-

'''
svakulenko
26 July 2017
'''

import requests
from bs4 import BeautifulSoup

from settings import *


TOPIC = {
           "narrative" : "This user is interested in popular media's perception and portrayal of US President Donald Trump.  He is interested in seeing examples that are especially humorous or surprising.",
           "title" : "Trump in media",
           "topid" : "RTS198",
           "description" : "How is Donald Trump perceived in various media."
        }

# e.g. GET https://www.googleapis.com/customsearch/v1?key=INSERT_YOUR_API_KEY&cx=017576662512468239146:omuauf_lfve&q=lectures
GOOGLE_SEARCH_API = 'https://www.googleapis.com/customsearch/v1?key=' + GOOGLE_API_KEY + '&cx=' + GOOGLE_CUSTOM_SE + '&q='


def search_google(query):
    doc = []
    resp = requests.get(GOOGLE_SEARCH_API+query)
    print (resp)
    results = resp.json()
    if 'items' in results.keys():
        for result in results['items']:
            title = result['title']
            print (title)
            doc.append(title)
            snippet = " ".join(result['snippet'].split(' ... ')[1:]).strip('\n')
            # print snippet
            doc.append(snippet)
            # print result['link']
            # print result
    # print '\n'
    return " ".join(doc)


def get_relevant_page(topic):
    link = search_google(topic)
    resp = requests.get(link)
    if resp:
        html_doc = resp.content
        # print html_doc
        soup = BeautifulSoup(html_doc, 'html.parser')
        
        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        print(text)


def test_get_relevant_page():
    get_relevant_page(TOPIC['description'])


def test_search_google():
    print (search_google(TOPIC['description']))


if __name__ == '__main__':
    test_search_google()
