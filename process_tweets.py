# -*- coding: utf-8 -*-
'''
svakulenko
24 july 2017
'''

from conceptualization import get_concepts_from_lotus


# sample tweets
true = "logging PowerShell defenders attackers"
false = "Security Cameras Surveillance Systems"


def lotus_recursive_call(original, found=None):
    '''
    '''
    concepts, found = get_concepts_from_lotus(original)
    print found
    print concepts
    
    if concepts:
        leftover = original.replace(found,"").strip()
        if leftover:
            lotus_recursive_call(leftover, found)


def main(tweets=[true, false]):
    # iterate over tweets
    for tweet in tweets:
        print tweet
        print '\n'
        lotus_recursive_call(tweet)
        print '\n'


if __name__ == '__main__':
    main()