import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN
from handlers import preferences_router

logging.basicConfig(level=logging.INFO)

async def main():
    # Создаем хранилище состояний для FSM
    storage = MemoryStorage()
    
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=storage)

    @dp.message(CommandStart())
    async def start_handler(message: types.Message):
        await message.answer("Привет! Я бот на aiogram 3.")

    @dp.message(Command("help"))
    async def help_handler(message: types.Message):
        await message.answer("Это команда /help. Чем могу помочь?")

    # Подключаем роутер для предпочтений
    dp.include_router(preferences_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 