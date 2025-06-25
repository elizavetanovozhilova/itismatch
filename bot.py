import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from config import API_TOKEN
from handlers import router as handlers_router
from db import create_pool

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any

logging.basicConfig(level=logging.INFO)

# Middleware для доступа к БД внутри хендлеров
class DBMiddleware(BaseMiddleware):
    def __init__(self, pool):
        self.pool = pool

    async def __call__(
        self,
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: Dict[str, Any]
    ) -> Any:
        data["db_pool"] = self.pool
        return await handler(event, data)

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Подключение к базе данных
    db_pool = await create_pool()

    # Устанавливаем middleware
    handlers_router.message.middleware(DBMiddleware(db_pool))

    # Подключаем все хендлеры
    dp.include_router(handlers_router)

    # Старт бота
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
