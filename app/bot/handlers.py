import logging
from aiogram import Router, types
from aiogram.filters.command import CommandStart
from app.db.tables import Chat


router = Router()


@router.message(CommandStart())
async def say_hi(message: types.Message):
    chat = await Chat.objects().get_or_create(
        Chat.chat_id == int(message.chat.id) & Chat.chat_type == message.chat.type
    )
    chat_type = chat.chat_type.title()
    logging.info(
        f"Chat ({chat_type}) already exists" if not chat._was_created else f"New chat ({chat_type}) is now created"
    )
