## [TWINT](https://github.com/twintproject/twint) Flask-Celery Server
Optimized tweets scraping and storing to Elasticsearch

### See also [Twint Kibana](https://github.com/Nedja995/twint_kibana)

#### Requirements
- Python3, [Twint](https://github.com/twintproject/twint), Flask, Celery
- Elasticsearch
- RabitMQ
- (optional) Flower 

#### Run

1. Run Celery worker: `$ celery -A app.celery worker --loglevel=info --concurrency=4`

2. Run Flask server: `$ python3 app.py`

- (optional) Monitor Celery with Flower: `$ celery -A app.celery flower --broker='pyamqp://guest@localhost//'`

#### Use

1. Create ES index with [index-tweets.json](elasticsearch/index-tweets.json)

2. Start tweets fetching
```
  POST  http://localhost:5000/fetch
  {
    "search": "<keyword>",
    "since": "2019-2-1",
    "until": "2019-3-1",
    "elasticsearch": "localhost:9200",
    "index_tweets": "<es index name>"
  }
```
