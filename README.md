### [TWINT](https://github.com/twintproject/twint) Flask-Celery Server
Optimized tweets scraping

#### See also [Twint Kibana](https://github.com/Nedja995/twint_kibana)

#### Requirements
- Python3, [Twint](https://github.com/twintproject/twint), Flask, Celery
- Elasticsearch(v7)
- RabitMQ
- (optional) Flower 

#### Run server

1. Run Celery workers: 
- `$ celery worker --app=worker.celery --hostname=worker.fetching@%h --queues=fetching --loglevel=info`
- (Optional) task for reporting progress if it is implemented `$ celery worker --app=worker.celery --hostname=worker.saving@%h --queues=saving --loglevel=info`

2. Run Flask server: `$ python3 app.py`

- (Optional) Monitor Celery with Flower: `$ celery -A app.celery flower --broker='pyamqp://guest@localhost//'`

#### Use

1. Create ES index with [index-tweets.json](elasticsearch/index-tweets.json)

2. Start tweets fetching
- arguments are mapped to [twint config](https://github.com/twintproject/twint/blob/master/twint/config.py)
- I mainly use it with elasticsearch so I did not test with other arguments
- Since and Until and Search/User are required
```
  POST  http://localhost:5000/fetch
  {
    "Since": "2019-2-1",
    "Until": "2019-3-1",
    "Search": "<keyword>",
    // or
    "User": "<username>"
    "Elasticsearch": "localhost:9200",
    "Index_tweets": "<es index name>"
  }
```
