import logging
import asyncio
import os
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get('API_TOKEN')

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.reply(
        "Привет! 👋\n"
        "Я умный бот с погодой и ИИ-анализом.\n"
        "Команды: /weather, /currency, /movie, /sentiment, /help")

@dp.message(Command("help"))
async def send_help(message: Message):
    await message.reply("Напиши мне что угодно — я проанализирую тональность и отвечу!")

@dp.message(Command("stop"))
async def stop_bot(message: Message):
    await message.reply("Пока! Бот остановлен.")

from api_weather import get_weather

@dp.message(Command("weather"))
async def weather_handler(message: Message):
    # Для простоты — Москва. В реальности используйте geopy для города
    await message.reply(get_weather(55.7558, 37.6173))

from ai_model import ai_response

@dp.message(Command("ai"))
async def ai_handler(message: Message):
    text = message.text.replace("/ai ", "")
    await message.reply(ai_response(text))

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())