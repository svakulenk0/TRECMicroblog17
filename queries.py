'''
21 July 2017
svakulenko
'''

multi_weighted = {
                    "query": {
                        "multi_match" : {
                            "fields": [ "title_stem", 'description_stem', 'narrative_stem']
                        }
                    }
                 }