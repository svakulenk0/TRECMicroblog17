# -*- coding: utf-8 -*-
'''
svakulenko
23 july 2017
'''
import json
import nltk

from settings import *
from conceptualization import *
from tweet_preprocess import MYSTOPLIST


def main(file=TOPICS):
    # iterate over topics
    with open(file, "r") as f:
        topics_json = json.load(f)
        for topic in topics_json:
            
            title = topic['title']

            # remove punctuation
            title = re.sub('[,."?\:…;!#()]', '', title)
            # tokenize
            # tokens = re.findall(r"\w+|[^\w\s]", title, re.UNICODE)
            # tokens = nltk.word_tokenize(title)
            tokens = title.split(' ')
            # print tokens
            # remove stopwords
            title = " ".join([token for token in tokens if token not in MYSTOPLIST])

            description = topic['description']
            narrative = topic['narrative']
            # lookup concepts
            print title
            print description
            print narrative

            concepts, text = get_concepts_from_lotus(title)
            print text
            print concepts
            
            if concepts:
                left = title.replace(text,"").strip()
                if left:
                    concepts, text = get_concepts_from_lotus(left)
                    print text
                    print concepts

                left2 = left.replace(text,"").strip()
                if left2:
                    concepts, text = get_concepts_from_lotus(left2)
                    print text
                    print concepts

            print '\n'


if __name__ == '__main__':
    main()