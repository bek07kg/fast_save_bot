import yt_dlp
import asyncio
import os

# Настройки для извлечения информации без скачивания самого файла
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'referer': 'https://www.tiktok.com/',
    'geo_bypass': True,
    # Добавляем таймаут и принудительный ipv4 (иногда ipv6 глючит на Windows)
    'source_address': '0.0.0.0', 
    'nocheckcertificate': True,
}

async def get_video_info(url: str):
    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Используем run_in_executor, чтобы не блокировать бота
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            return info
    except Exception as e:
        # Это выведет реальную причину ошибки в консоль VS Code
        print(f"ОШИБКА YT-DLP: {e}") 
        return None

def get_formats(info):
    """
    Выбираем только видео-форматы с разным качеством (360p, 720p и т.д.)
    """
    formats = []
    # Нам нужны форматы, где есть и видео, и аудио (или только видео для YouTube)
    seen_heights = set()
    
    if 'formats' in info:
        for f in info['formats']:
            # Нам интересны только форматы с видео (у которых есть высота 'height')
            height = f.get('height')
            if height and height not in seen_heights:
                # Добавляем в список только уникальные разрешения
                formats.append({
                    'format_id': f['format_id'],
                    'resolution': f'{height}p',
                    'ext': f['ext']
                })
                seen_heights.add(height)
    
    # Сортируем от меньшего к большему
    return sorted(formats, key=lambda x: int(x['resolution'][:-1]))

# Путь к папке для загрузок
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

async def download_video(url: str, format_id: str):
    loop = asyncio.get_event_loop()
    
    # Мы говорим: возьми выбранное видео (format_id) и добавь к нему лучшее аудио
    # Или просто скачай лучшее готовое видео, если что-то пошло не так
    file_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    
    opts = {
        'format': f'{format_id}+bestaudio/best', 
        'outtmpl': file_path,
        'quiet': True,
        'noplaylist': True,
        'merge_output_format': 'mp4',
        # Указываем путь к ffmpeg явно, если он лежит в папке с ботом
        'ffmpeg_location': '.', 
    }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        # download=True физически скачивает файл
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
        filename = ydl.prepare_filename(info)
        
        # yt-dlp может изменить расширение при склейке на .mp4
        # Нам нужно убедиться, что мы возвращаем правильное имя файла
        actual_filename = filename.rsplit('.', 1)[0] + ".mp4"
        return actual_filename

async def download_audio(url: str):
    """Скачивает только аудио в формате mp3"""
    loop = asyncio.get_event_loop()
    file_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': file_path,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
        # Возвращаем путь к mp3 файлу
        return ydl.prepare_filename(info).rsplit('.', 1)[0] + ".mp3"

