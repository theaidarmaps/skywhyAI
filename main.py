import logging
import asyncio
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from dotenv import load_dotenv

from api_weather import weather_rt
from tonality_analysis import tonality_rt
from ai_integration import ai_router


load_dotenv()

TOKEN = os.environ.get('API_TOKEN')

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_routers(weather_rt, tonality_rt, ai_router)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(f'Привет, {message.from_user.username}! Для просмотра всех команд напишите /help')


@dp.message(Command('help'))
async def help_handler(message: Message) -> None:
    weather_help_text = '/weather - Спрашивает город, затем присылает погоду на следующие 5 дней'
    sentiment_help_text = '/sentiment {Сообщение} - Определяет тональность введенного ранее сообщения'
    ai_help_text = '/ai - Ожидает текстовый запрос, затем присылает ответ от нейронной сети (Gemini 3 flash)'

    await message.answer(f'Список всех команд:\n{weather_help_text}\n{sentiment_help_text}\n{ai_help_text}')


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
