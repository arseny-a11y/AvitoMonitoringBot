from aiogram import Dispatcher,Bot
from aiogram.client.session.aiohttp import AiohttpSession
from config.config import settings
from bot.handlers.monitor import monitor_router
from database.database import init_db
import logging
import asyncio
import warnings

warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed transport")

async def main():
    logging.basicConfig(level=logging.INFO)

    session = AiohttpSession(proxy=settings.PROXY)

    bot = Bot(settings.TOKEN, session=session)
    dp = Dispatcher()

    await init_db()

    dp.include_router(monitor_router)

    try:
        print("Бот запущен!")
        await bot.delete_webhook(drop_pending_updates=True)
        
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt,SystemExit):
        print("Бот остановлен!")        
