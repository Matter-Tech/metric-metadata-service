"""

This is the Celery Beat schedule for Cron Jobs.
Celery Beat schedules tasks according to the settings below.

"""

from celery.schedules import crontab
from matter_task_queue import CELERY_LOW_PRIORITY_QUEUE

CELERYBEAT_SCHEDULE = {
    "items.hello_world_item_back_task": {
        "task": f"{CELERY_LOW_PRIORITY_QUEUE}:items.hello_world_item_back_task",
        "schedule": crontab(minute="*/1"),
        "args": ("Test Message",),
    },
}
