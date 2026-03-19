from aiogram import Router, types, F
from core.downloader import get_video_info
from keyboards.inline import get_format_selection

router = Router()

# Временное хранилище для данных (в идеале использовать БД или Redis, но для начала сойдет и словарь)
user_data = {}

@router.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    url = message.text
    wait_msg = await message.answer("⏳ Анализирую ссылку...")
    
    video_info = await get_video_info(url)
    
    if not video_info:
        await wait_msg.edit_text("❌ Не удалось получить данные. Проверь ссылку.")
        return

    # Сохраняем инфо о видео, чтобы не запрашивать его дважды
    user_data[message.from_user.id] = video_info
    
    title = video_info.get('title', 'Видео')
    
    await wait_msg.delete() # Удаляем сообщение о загрузке
    await message.answer(
        f"✅ <b>{title}</b>\n\nЧто именно хочешь скачать?",
        reply_markup=get_format_selection(),
        parse_mode="HTML"
    )
    