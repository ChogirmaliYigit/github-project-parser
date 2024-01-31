from aiogram import Router, types


router = Router()


@router.message()
async def say_hi(message: types.Message):
    await message.answer("Hi. Welcome!")
