from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def get_format_selection():
    """Первый шаг: выбор между Видео и Аудио"""
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🎬 Видео", callback_data="type_video"),
        types.InlineKeyboardButton(text="🎧 Аудио (MP3)", callback_data="type_audio")
    )
    return builder.as_markup()

def get_quality_buttons(formats):
    """Второй шаг: если выбрано видео, показываем доступные разрешения"""
    builder = InlineKeyboardBuilder()
    
    # formats приходит из нашего downloader.py
    for f in formats:
        res = f['resolution']
        f_id = f['format_id']
        # Сохраняем format_id в callback_data, чтобы потом знать, что скачивать
        builder.add(types.InlineKeyboardButton(
            text=res, 
            callback_data=f"quality_{f_id}"
        ))
    
    builder.adjust(2) # Кнопки в 2 колонки
    return builder.as_markup()
    