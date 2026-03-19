from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()  # <--- Вот эта строчка обязательна!

@router.message(CommandStart())
async def command_start_handler(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}! 👋\n"
        "Я помогу тебе скачать видео или аудио из YouTube, TikTok и Instagram.\n\n"
        "Просто **отправь мне ссылку** на ролик!"
    )
    