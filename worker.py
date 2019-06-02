import os
from celery import Celery
from config import config

CELERY_BROKER_URL = config['CELERY_BROKER_URL']

celery = Celery('flask_server', backend='amqp')
celery.conf.update({
    'broker_url': config['CELERY_BROKER_URL'],
    'backend': 'amqp', 
    'imports': (
        'tasks',
    ),
    'task_routes': {
        'fetch': {'queue': 'fetching'}
        # 'save': {'queue': 'saving'}
    },
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json']})
