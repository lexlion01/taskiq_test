from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
import asyncio
import logging.config
from log_config.log_settings import logging_config
from config_reader import get_config, BotConfig
from handlers import get_routers
from scheduler.taskiq_broker import broker
from os import name as osname



logging.config.dictConfig(logging_config)
ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query', 'my_chat_member']

logger = logging.getLogger(__name__)
bot_config = get_config(BotConfig, "bot")

if osname == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def on_startup(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)


async def on_shutdown(bot: Bot, dp: Dispatcher) -> None:
    logger.info(f"Shutting down")
    await bot.delete_webhook(drop_pending_updates=True)
    # Закрываем сессию бота, освобождая ресурсы
    await bot.session.close()
    await dp.storage.close()



async def main():
    logger.info('Starting up')

    dp = Dispatcher()
    logger.info('Connecting routers')
    dp.include_routers(*get_routers())
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    logger.info('Setting up middlewares')
    logger.info('Initializing bot')

    bot = Bot(token=bot_config.token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await broker.startup()

    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        logger.info("Starting the main event loop.")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Received exit signal via keyboard interrupt')


