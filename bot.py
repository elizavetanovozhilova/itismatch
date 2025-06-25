import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from config import API_TOKEN

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start_handler(message: types.Message):
        await message.answer("Привет! Я бот на aiogram 3.")

    @dp.message(Command("help"))
    async def help_handler(message: types.Message):
        await message.answer("Это команда /help. Чем могу помочь?")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 