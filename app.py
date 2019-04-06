from __future__ import absolute_import
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from celery import Celery, group
import twint
import configparser

dtformat = "%Y-%m-%d"

config = configparser.ConfigParser()
config.read('config.ini')

if config["DEFAULT"]["DEV"]:
    config = config['DEV']
else:
    config = config['PROD']

app = Flask('twint_server')
# import settings
#app.config.from_object(settings)

def make_celery(app):
    celery = Celery(app.import_name, \
                    backend='rpc://', \
                    broker=config['CELERY_BROKER_URL'])

    #celery.conf.update(app.config)
    
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

@celery.task(name="tasks.fetch")
def fetch_task(args):
    #search, since, until, elasticsearch, index_tweets
    # Configure
    c = twint.Config()
    c.Search = args['search']
    c.Since = args['since']
    c.Until = args['until']
    c.Count = True
    c.Elasticsearch = args['elasticsearch']
    c.Index_tweets = args['index_tweets']
    # Run
    twint.run.Search(c)
    return "Finished"

@app.route("/fetch", methods=['POST'])
def fetch_tweets():
    print("run")
   
    search = request.json['search']
    since = request.json['since']
    until = request.json['until']
    elasticsearch = request.json['elasticsearch']
    index_tweets = request.json['index_tweets']
    # args.maximum_instances = 4 # depends on worker concurency parametar
    request_days = 1#request.json['request_days']
    since = datetime.strptime(since, dtformat).date()
    until = datetime.strptime(until, dtformat).date()
    # Prepaire arguments array.
    end = since + timedelta(days=request_days)
    arguments = [{
        'search': search,
        'since': since.strftime(dtformat),
        'until': end.strftime(dtformat),
        'elasticsearch': elasticsearch,
        'index_tweets': index_tweets,
        'id': 0}]
    i = 1
    while end < until:
        since = since + timedelta(days=request_days)
        end = since + timedelta(days=request_days)
        if end > until:
            end = until
        arguments.append({
        'search': search,
        'since': since.strftime(dtformat),
        'until': end.strftime(dtformat),
        'elasticsearch': elasticsearch,
        'index_tweets': index_tweets,
        'id': i})
        i += 1
    # print("Ranges to fetch {}".format(len(arguments)))

    jobs = group(fetch_task.s(item) for item in arguments)
    result = jobs.apply_async()

    return "Fetching started. Processes to finish {} ".format(len(arguments))

if __name__ == "__main__":
    from os import environ
    port = int(environ.get("PORT", config['PORT']))
    app.run(host=config['HOST'], port=port, debug=config['DEV'])