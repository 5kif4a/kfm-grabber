import os
from os.path import join, dirname

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SECRET_KEY = os.environ.get("SECRET_KEY")
SENTRY_DSN = os.environ.get("SENTRY_DSN")
INTERVAL = int(os.environ.get('INTERVAL'))


class Config(object):  # for APSCHEDULER
    JOBS = [
        {
            'id': 'job1',
            'func': 'main:update',
            'trigger': 'interval',
            'minutes': INTERVAL
        }
    ]
