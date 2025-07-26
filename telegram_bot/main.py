import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database import Database
from handlers import setup_handlers

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

if not BOT_TOKEN:
    logger.error("BOT_TOKEN не найден в переменных окружения!")
    exit(1)

async def main():
    """Основная функция запуска бота"""
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Инициализация базы данных
    db = Database()
    await db.init_db()
    
    # Настройка обработчиков
    setup_handlers(dp, db)
    
    logger.info("Бот запущен!")
    
    try:
        # Запуск поллинга
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        exit(1)