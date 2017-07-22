'''
title is the field for exact matching
'''

mapping_exact_title = '''
{  
  "mappings":{  
    "topics":{  
      "properties":{  
        "title":{  
          "type":"string",
          "index":"not_analyzed"
        }
      }
    }
  }
}'''

mapping_td = '''
{  
  "mappings":{  
    "topics":{  
      "properties":{  
        "td": {
          "type": string,
          "analyzer": english
        },
      }
    }
  }
}'''

english_3 = {
  "settings": {
    "analysis": {
      "filter": {
        "custom_english_stemmer": {
          "type": "stemmer",
          "name": "english"
        }
      },
      "analyzer": {
        "custom_lowercase_stemmed": {
          "tokenizer": "standard",
          "stopwords": [ "and", "the", "of" ],
          "filter": [
            "lowercase",
            "custom_english_stemmer"
          ]
        }
      }
    }
  },
  "mappings": {
    "topics": {
      "properties": {
        "title": {
          "type": "string",
          "analyzer": "custom_lowercase_stemmed"
        },
        "description": {
          "type": "string",
          "analyzer": "custom_lowercase_stemmed"
        },
        "narrative": {
          "type": "string",
          "analyzer": "custom_lowercase_stemmed"
        }
      }
    }
  }
}

create_index_body = {
      'settings': {
        # just one shard, no replicas for testing
        'number_of_shards': 1,
        'number_of_replicas': 0,
      },
      'mappings': {
        'topics': {
          'properties': {
            'title': {'type': 'text', 'analyzer': 'english'},
            'description': {'type': 'text', 'analyzer': 'english'},
            'narrative': {'type': 'text', 'analyzer': 'english'}
          }
        },
        'tweets': {
          'properties': {
            'tweet': {'type': 'text', 'analyzer': 'english'},
          }
        }
      }
    }



mapping_keyword_title = '''
{  
  "mappings":{  
    "topics":{  
      "properties":{  
        "title":{  
          "type":"keyword"
        },
        "description": {
          "type": string,
          "analyzer": english
        },
        "narrative": {
          "type": string,
          "analyzer": english
        },
      }
    }
  }
}'''