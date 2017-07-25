# TREC 2017 Real-Time Summarization

Evaluation will take place from July 25 00:00:00 UTC to August 3 23:59:59 UTC

188 topics provided by the organizers in JSON format. A sample topic contains title, description and narrative fields.

Scenario A. Push notifications should be:

* relevant (on topic) -- tweet-query similarity ranking
* timely (provide updates as soon after the actual event occurrence as possible) -- Kafka, RabbitMQ queues
* novel (users should not be pushed multiple notifications that say the same thing) -- results diversification, tweet-tweet similarity

## Requirements

* tweepy
* elasticsearch
* nltk: nltk.download() -> stopwords
* rdflib

## Usage

* Populate ES index with topics dumped in JSON file

load_topics_from_file()

* Monitor Twitter stream for TREC topics:
topic_client.py

* Test sample queries against the TREC topics:
es_search.py


## Setup

* Get client ids for the TREC API (save to CLIENT_IDS in settings.py)


register_clients()


* Get topics from the TREC API


get_topics()



## Acknowledgements


## References

1. TREC Real-Time Summarization Track http://trecrts.github.io