from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from app.config_reader import Settings


async def on_startup_notify(bot: Bot, config: Settings):
    for admin in config.admins:
        try:
            bot_properties = await bot.me()
            await bot.send_message(
                int(admin),
                "\n".join([
                    "<b>Bot ishga tushdi.</b>\n",
                    f"<b>Bot ID:</b> {bot_properties.id}",
                    f"<b>Bot Username:</b> @{bot_properties.username}"
                ])
            )
        except TelegramBadRequest:
            pass
