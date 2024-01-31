import sys
import logging
from aiogram import Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp.web import run_app
from aiohttp.web_app import Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from piccolo.engine import engine_finder
from app.bot.handlers import router
from app.bot.notify_admin import on_startup_notify
from app.bot.loader import dispatcher, bot
from app.scraper.github_projects import get_github_projects
from app.db.tables import PROJECT_TABLES
from app.config_reader import Settings


async def connect_db(config: Settings, close=False, persist=True) -> None:
    db = engine_finder(config.piccolo_conf)

    if db.engine_type == 'sqlite':
        if close:
            return

        if not persist:
            for table in reversed(PROJECT_TABLES):
                await table.alter().drop_table(if_exists=True)

        for table in PROJECT_TABLES:
            await table.create_table(if_not_exists=True)
    else:
        if close:
            return await db.close_connection_pool()

        await db.start_connection_pool()


async def aiogram_on_startup_polling(b: Bot, scheduler: AsyncIOScheduler, config: Settings) -> None:
    await connect_db(config, persist=True)
    await b.set_webhook(f"{config.webhook_base_url}/webhook")
    await on_startup_notify(bot=b, config=config)

    scheduler.add_job(
        get_github_projects, 'interval', seconds=20, kwargs={"bot": bot, "config": config}
    )
    scheduler.start()


async def aiogram_on_shutdown_polling(b: Bot, scheduler: AsyncIOScheduler, config: Settings):
    await connect_db(config, close=True)
    await b.delete_webhook(drop_pending_updates=True)
    scheduler.shutdown(wait=False)


def main():
    dispatcher.startup.register(aiogram_on_startup_polling)
    dispatcher.shutdown.register(aiogram_on_shutdown_polling)
    dispatcher.include_router(router)

    scheduler = AsyncIOScheduler()
    config = Settings()
    dispatcher['scheduler'] = scheduler
    dispatcher["b"] = bot
    dispatcher['config'] = config

    app = Application()
    app["bot"] = bot

    SimpleRequestHandler(dispatcher=dispatcher, bot=bot).register(app, path="/webhook")
    setup_application(app, dispatcher, bot=bot)

    run_app(app, host="127.0.0.1", port=8085)


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        main()
    except KeyboardInterrupt:
        logging.info("Bot stopped!")
