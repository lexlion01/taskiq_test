from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import logging
from scheduler.tasks import simple_task
logger = logging.getLogger('root')
admin_router = Router()


@admin_router.message(Command(commands='task'))
async def on_message1(message: Message, *_):
    try:
        print('show time\n\n\n')
        await simple_task.kiq()
    except:
        logger.exception('Что-то пошло не так')

