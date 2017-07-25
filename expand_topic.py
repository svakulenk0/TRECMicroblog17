# -*- coding: utf-8 -*-
'''
svakulenko
25 july 2017
'''

from conceptualization import lotus_recursive_call, lookup_nns, loop_concept_expansion


TOPIC = {
           "narrative" : "@SwiftOnSecurity is a great twitter account about IT security that targets a broad audience. Tweets from the similar accounts on the IT security topic are also relevant.",
           "title" : "IT security",
           "topid" : "RTS219",
           "description" : "News and reflections about IT security."
        }

# sample tweets
TWEET = "logging PowerShell defenders attackers"


def discover_topic(topic=TOPIC):
    title = topic['title']
    print title
    
    topic_concepts = lotus_recursive_call(title)
    
    for concept_uri in topic_concepts:
        loop_concept_expansion(concept_uri)


if __name__ == '__main__':
    discover_topic()
