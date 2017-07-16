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