import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, links, callbacks

async def main():
    # Настраиваем логи, чтобы видеть ошибки в консоли
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Инициализируем бота
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем роутеры (наши обработчики)
    dp.include_router(start.router)
    dp.include_router(links.router)
    dp.include_router(callbacks.router)

    # Запускаем прослушивание сообщений
    print("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
