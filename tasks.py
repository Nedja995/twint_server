import time
from worker import celery
from config import config
import twint
from arguments import TwintArguments

@celery.task(name='fetch')
def fetch(args):
    print("Start fetch task %s %s -> %s" % 
        (args.id, config.Since, config.Until))
    # Merge user arguments with default Twint config
    config = TwintArguments()
    config.__dict__.update(args)
    # Run
    twint.run.Search(config)
    # Finished
    return "Fetch task finished %s %s -> %s" % 
        (args.id, config.Since, config.Until)

# # Save/report progress if you want or example to firebase
# @celery.task(name='save')
# def save(args):
#     db = firebase.database()
#     # Make process entry on firebase
#     db.child("Processes").child(args['id']).set(args)
#     return "Progress saved"