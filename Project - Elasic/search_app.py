from flask import Flask, request
from markupsafe import escape
from flask import render_template
from elasticsearch import Elasticsearch
import math

ELASTIC_PASSWORD = "Dr4wPzShPCwW5inOXV4M"

es = Elasticsearch("https://localhost:9200", http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    page_size = 10
    keyword = request.args.get('keyword')
    if request.args.get('page'):
        page_no = int(request.args.get('page'))
    else:
        page_no = 1

    body = {
        'size': page_size,
        'from': page_size * (page_no-1),

  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": keyword,
            "fields": ["name^5", "lyrics^2","artisit/brand^5", "album^3" ],
             "fuzziness": "AUTO"
          }
        }
      ],"should": [
         {
          "match_phrase": {
            "name":{
            "query": keyword,
         "slop": 1
          }
          }
        },  
        {
          "match_phrase": {
            "album":{
            "query": keyword,
         "slop": 1
          }
          }
        },
         {
          "match_phrase": {
            "lyrics":{
            "query": keyword,
         "slop": 1
          }
          }
        },
         {
          "match_phrase": {
            "artisit/brand":{
            "query": keyword,
         "slop": 1
          }
          }
        }
        ]
    }
  }
  #For sort the release date by release Date
#   , "sort": [
#     {
#       "releaseDate": {
#         "order": "asc"
#       }
#     }
#   ]
}


    #res = es.search(index='product', doc_type='', body=body)
    #res = es.search(index='product',  body=body)
    #res = es.search(index='recipe',  body=body)
    res = es.search(index='tablemusics',  body=body)
    hits = [{'id' : doc['_id'],'name': doc['_source']['name'], 'lyrics': doc['_source']['lyrics'], 'releaseDate': doc['_source']['releaseDate'] , 'artist/brand': doc['_source']['artist/brand'], 'url': doc['_source']['url']} for doc in res['hits']['hits']]
    #hits = [{'title': doc['_source']['title'], 'description': doc['_source']['description'], 'created': doc['_source']['created']} for doc in res['hits']['hits']]
    page_total = math.ceil(res['hits']['total']['value']/page_size)
    return render_template('search.html',keyword=keyword, hits=hits, page_no=page_no, page_total=page_total)

@app.route('/result')
def result():
    test = request.url.split('=');
    keyword = test[1]
    
    body = {
      "query": {
        "bool": {
          "must": [
              {
                "match": {
                  "_id": keyword
                }
              }
            
            ]
          }
        }    
    }

    res = es.search(index='tablemusics',  body=body)
    hits = [{'id' : doc['_id'],'name': doc['_source']['name'], 'lyrics': doc['_source']['lyrics'], 'releaseDate': doc['_source']['releaseDate'] , 'artist/brand': doc['_source']['artist/brand'], 'url': doc['_source']['url']} for doc in res['hits']['hits']]
    #hits = [{'title': doc['_source']['title'], 'description': doc['_source']['description'], 'created': doc['_source']['created']} for doc in res['hits']['hits']]
    return render_template('result.html', hits=hits)