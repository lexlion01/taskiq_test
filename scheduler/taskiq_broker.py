import logging

from taskiq import TaskiqScheduler, TaskiqEvents, TaskiqState
from taskiq_redis import RedisScheduleSource
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_nats import NatsBroker

logger = logging.getLogger('root')
broker = NatsBroker(servers=['nats://localhost:4222'], queue="taskiq_tasks", subject='test')

redis_source = RedisScheduleSource(url=f'redis://localhost:6379')

scheduler = TaskiqScheduler(broker, [redis_source, LabelScheduleSource(broker)])


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:

    logger.info("Starting scheduler...")

    state.logger = logger


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    state.logger.info("Scheduler stopped")