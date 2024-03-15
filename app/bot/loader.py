from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from app.config_reader import config


bot = Bot(token=config.bot_token, parse_mode=ParseMode.HTML)
dispatcher = Dispatcher()
