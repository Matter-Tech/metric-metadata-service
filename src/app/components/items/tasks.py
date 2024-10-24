import logging

from celery import shared_task
from matter_exceptions import DetailedException
from matter_observability.metrics import (
    LabeledGauge,
    gauge_value,
    measure_processing_time,
)
from matter_task_queue import (
    CELERY_DEFAULT_QUEUE,
    CELERY_LOW_PRIORITY_QUEUE,
    async_to_sync,
)

from app.common.celery.base_task import BaseAPITask

from .utils import some_back_processing_func, some_util_func


@shared_task(
    bind=True,
    name=f"{CELERY_DEFAULT_QUEUE}:items.hello_world_item_task",
    base=BaseAPITask,
    autoretry_for=(DetailedException,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 1},
)
@gauge_value(label="hello_world_item_task", use_push_gateway=True)
@measure_processing_time(label="hello_world_item_task_duration", use_push_gateway=True)
def hello_world_item_task(
    _,
    some_id: str,
    gauge: LabeledGauge,
):
    logging.info(f"Received this Id: {some_id}")
    some_value = 3
    gauge.set(some_value)

    async_to_sync(some_util_func)


@shared_task(
    bind=True,
    name=f"{CELERY_LOW_PRIORITY_QUEUE}:items.hello_world_item_back_task",
    base=BaseAPITask,
    autoretry_for=(DetailedException,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 1},
)
@gauge_value(label="hello_world_item_back_task", use_push_gateway=True)
@measure_processing_time(label="hello_world_item_back_task_duration", use_push_gateway=True)
def hello_world_item_back_task(
    _,
    some_id: str,
    gauge: LabeledGauge,
):
    logging.info(f"Received this Id: {some_id}")
    some_value = 2
    gauge.set(some_value)

    async_to_sync(some_back_processing_func)
