from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import BufferedInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import asyncio
import logging.config
from log_config.log_settings import logging_config
from config_reader import get_config, DbConfig, BotConfig, WebHookConfig
from handlers import get_routers
from scheduler.taskiq_broker import broker
from os import name as osname



logging.config.dictConfig(logging_config)
ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query', 'my_chat_member']

logger = logging.getLogger(__name__)
bot_config = get_config(BotConfig, "bot")
wh_config = get_config(WebHookConfig, 'webhook')


if osname == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def on_startup(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)

    await bot.set_webhook(f"{wh_config.base_webhook_url}{wh_config.webhook_path}",
                          secret_token=wh_config.webhook_secret,
                          certificate=BufferedInputFile.from_file(wh_config.webhook_ssl_cert),
                          allowed_updates=ALLOWED_UPDATES)



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
    app = web.Application()

    await broker.startup()

    webhook_request_handler = SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=wh_config.webhook_secret)
    webhook_request_handler.register(app, path=wh_config.webhook_path)
    setup_application(app, dp, bot=bot)
    logger.info('Starting app')
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=wh_config.web_server_host, port=wh_config.web_server_port)
    await site.start()
    logger.info(f'Ready to use\n\n       Started on  {site.name}!')

    try:
        while True:
            await asyncio.sleep(3600)
        # await asyncio.Event().wait()
    except asyncio.CancelledError:
        logger.info('Shutdown bot session..')
        await bot.session.close()
        logger.info('Shutdown dp storage ..')
        await dp.storage.close()


if __name__ == '__main__':
    try:
        logger.info("Starting the main event loop.")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Received exit signal via keyboard interrupt')


