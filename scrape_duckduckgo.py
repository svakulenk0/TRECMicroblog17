import requests
import json
from lxml import html
import time

from newspaper import Article

from settings import *



TOPIC = {
           "narrative" : "The user is an avid cycler and wants to follow any injuries to riders in this year's Tour de France race.",
           "title" : "Tour de France",
           "topid" : "RTS138",
           "description" : "What injuries happened in this year's Tour de France?"
        }


def search(keywords, max_results=None):
    url = 'https://duckduckgo.com/html/'
    params = {
        'q': keywords,
        's': '0',
    }

    yielded = 0
    while True:
        res = requests.post(url, data=params)
        doc = html.fromstring(res.text)

        results = [a.get('href') for a in doc.cssselect('#links .links_main a')]
        for result in results:
            yield result
            time.sleep(0.1)
            yielded += 1
            if max_results and yielded >= max_results:
                return

        try:
            form = doc.cssselect('.results_links_more form')[-1]
        except IndexError:
            return
        params = dict(form.fields)


def get_relevant_article(topic):
    urls = search(topic, max_results=5)
    for url in urls:
        # print(url)
        a = Article(url, language='en')
        try:
            a.download()
            a.parse()
            title = a.title
            text = a.text
            return ' '.join([title, text])
        except:
            pass


def test_get_relevant_article():
    get_relevant_article(TOPIC['description'])


def test_search(keywords=TOPIC['description'], max_results=1):
    results = search(keywords, max_results)
    for result in results:
        print(result)


def test_get_articles_for_topics(file=TOPICS, limit=5):
    with open(file, "r") as f:
        topics_json = json.load(f)
        for topic in topics_json[:limit]:
            topic_description = topic['description']
            print(topic_description)
            print(get_relevant_article(topic_description))
            print('\n')


if __name__ == '__main__':
    test_get_articles_for_topics()
