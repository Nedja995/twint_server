from __future__ import absolute_import
from datetime import datetime, timedelta
import time
import copy
import json
# dependencies
from flask import Flask, jsonify, request
from celery import group
# import uuid
# project dependencies
from config import config
from tasks import fetch
from worker import celery

# Date format from arguments. Also required for Twint
dtformat = "%Y-%m-%d"

#
# Initialize Flask
app = Flask('twint_server')

# Development on localhost
if config['ALLOW_CORS']:
    from flask_cors import CORS
    CORS(app)

class Empty(object):
    pass

#
# REST Endpoint
@app.route("/fetch", methods=['POST'])
def fetch_tweets():
    print("Fetching request")
    config = Empty()
    config.__dict__ = request.json
    #
    # Required arguments
    since = config.Since
    until = config.Until
    # args.maximum_instances = 4 # depends on worker concurency parametar
    request_days = 1 #request.json['request_days']
    since_iter = datetime.strptime(since, dtformat).date()
    until = datetime.strptime(until, dtformat).date()
    #
    # Prepaire arguments for processes.
    arguments = []
    end = since_iter + timedelta(days=request_days)
    i = 0
    while end < until:
        if i > 0:
            since_iter = since_iter + timedelta(days=request_days)
            end = since_iter + timedelta(days=request_days)
        if end > until:
            end = until
        argument = copy.deepcopy(config)
        argument.Since = since_iter.strftime(dtformat)
        argument.Until = end.strftime(dtformat)
        argument.id = i
        arguments.append(argument.__dict__)
        i += 1
    print("Number of processes %s" % len(arguments))
    #
    # Make processes with arguments
    jobs = group(fetch.s(item) for item in arguments)
    # Start jobs
    jobsResult = jobs.apply_async()

    # Return info
    return "Fetching started\n%s\n%s -> %s\nProcesses count: %s" % (config.Search, config.Since, config.Until, len(arguments))

    # #
    # # Feature to track state in two way:
    # # 1. Return celery processes ids 
    # # 2. Use aditional task to save celery ids to server in group
    # #
    # ids = []
    # for i in jobsResult:
    #     ids.append({"id": i.id, "status": "PENDING"})
    
    # #
    # # 1. Return celery processes ids 
    # return jsonify(ids)

    # #
    # # 2. Use aditional task to save celery ids to server in group
    # group_id = uuid.uuid4()
    # res = save.s({
    #     "name": search,
    #     "status": "STARTED",
    #     "progress": 0,
    #     "id": group_id,
    #     "ids": ids,
    #     "since": since,
    #     "until": until.strftime(dtformat),
    #     "elasticsearch": elasticsearch,
    #     "index_tweets": index_tweets,
    #     "created_at": datetime.now()
    # }).apply_async()
    # return jsonify(group_id)

if __name__ == "__main__":
    from os import environ
    port = int(environ.get("PORT", config['PORT']))
    app.run(host=config['HOST'], port=port, debug=config['FLASK_DEBUG'])