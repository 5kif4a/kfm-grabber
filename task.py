from celery import Celery
from celery.schedules import crontab
from settings import *


def make_celery(app):
    app.config['CELERYBEAT_SCHEDULE'] = {
        'periodic_task-every-hour': {
            'task': 'periodic_task',
            'schedule': crontab(minute=DELAY)
        }
    }

    celery = Celery(app.import_name, broker=CELERY_BROKER_URL)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
