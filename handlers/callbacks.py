import os
import logging
from aiogram import Router, types, F
from core.downloader import download_video, download_audio
from handlers.links import user_data

router = Router()

@router.callback_query(F.data.startswith("quality_"))
async def process_download_video(callback: types.CallbackQuery):
    format_id = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    if user_id not in user_data:
        await callback.answer("❌ Данные истекли. Скинь ссылку еще раз.", show_alert=True)
        return

    url = user_data[user_id]['webpage_url']
    status_msg = await callback.message.edit_text("⏳ Скачиваю видео на сервер... Пожалуйста, подожди.")

    file_path = None
    try:
        # 1. Скачиваем файл
        file_path = await download_video(url, format_id)
        
        # 2. Проверяем, существует ли файл
        if not os.path.exists(file_path):
            raise Exception("Файл не был найден после скачивания.")

        # 3. Проверяем размер (лимит 50 МБ)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        if file_size_mb > 50:
            await status_msg.edit_text(
                f"⚠️ <b>Файл слишком большой!</b>\n"
                f"Размер: {round(file_size_mb, 1)} МБ.\n"
                f"Лимит Bot API: 50 МБ.\n\n"
                f"<i>Скоро мы переедем на сервер и снимем это ограничение!</i>",
                parse_mode="HTML"
            )
        else:
            await status_msg.edit_text("🚀 Загружаю видео в Telegram...")
            video_file = types.FSInputFile(file_path)
            await callback.message.answer_video(
                video_file, 
                caption=f"🎬 {user_data[user_id].get('title')}\n📥 Размер: {round(file_size_mb, 1)} МБ"
            )
            await status_msg.delete()

    except Exception as e:
        logging.error(f"Error in video download: {e}")
        await callback.message.answer(f"❌ Произошла ошибка: {str(e)[:100]}")
    
    finally:
        # 4. Удаляем файл в любом случае
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

@router.callback_query(F.data == "type_audio")
async def process_download_audio(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_data:
        await callback.answer("❌ Скинь ссылку заново.")
        return

    url = user_data[user_id]['webpage_url']
    status_msg = await callback.message.edit_text("🎵 Конвертирую в MP3...")

    file_path = None
    try:
        file_path = await download_audio(url)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

        if file_size_mb > 50:
            await status_msg.edit_text(f"⚠️ Аудио слишком тяжелое ({round(file_size_mb, 1)} МБ).")
        else:
            audio_file = types.FSInputFile(file_path)
            await callback.message.answer_audio(
                audio_file, 
                caption=f"🎧 {user_data[user_id].get('title')}"
            )
            await status_msg.delete()

    except Exception as e:
        await callback.message.answer(f"❌ Ошибка аудио: {e}")
    
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            