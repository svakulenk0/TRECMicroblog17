# TREC 2017 Real-Time Summarization

Evaluation will take place from July 25 00:00:00 UTC to August 3 23:59:59 UTC

Scenario A (push notifications).

Push notifications should be:

* relevant (on topic)
* timely (provide updates as soon after the actual event occurrence as possible)
* novel (users should not be pushed multiple notifications that say the same thing)


## Requirements

* tweepy
* elasticsearch

## Usage

* Monitor Twitter stream for TREC topics:
topic_client.py

* Test sample queries against the TREC topics:
es_search.py

## Acknowledgements


## References

1. http://trecrts.github.io