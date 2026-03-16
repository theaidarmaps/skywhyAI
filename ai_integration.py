import os

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from google import genai

from dotenv import load_dotenv
from google.genai.errors import ClientError


load_dotenv()

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
client = genai.Client(api_key=GEMINI_API_KEY)

ai_router = Router()


class Form(StatesGroup):
    waiting = State()


@ai_router.message(Command('ai'))
async def ai_answer(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Отменить', callback_data='cancel_answer')]
    ], resize_keyboard=True, one_time_keyboard=True)

    msg = await message.answer('Напиши свой запрос', reply_markup=keyboard)
    await state.update_data(button_message_id=msg.message_id)
    await state.set_state(Form.waiting)


@ai_router.message(Form.waiting)
async def ai_answer_handler(message: Message, state: FSMContext):
    try:
        response = client.models.generate_content(
            model='gemini-3-flash-preview', contents=message.text
        )
        response_text = response.text

        if not response_text:
            return

        if len(response_text) <= 4096:
            await message.answer(response.text)
            return

        response_parts = []

        while len(response_text) > 0:
            if len(response_text) <= 4096:
                response_parts.append(response_text)
                response_text = ''
            else:
                chunk = response_text[:4096]
                last_newline = chunk.find('\n')
                if last_newline != -1:
                    response_parts.append(chunk[:last_newline])
                    response_text = response_text[last_newline+1:]
                else:
                    response_parts.append(chunk)
                    response_text = response_text[4096]

        for part in response_parts:
            if part:
                await message.answer(part)

    except TelegramBadRequest as br:
        print('error: ' + br.message)
        await message.answer('Произошла ошибка. Повторите попытку позже')
    except ClientError as ce:
        if ce.code == 400:
            await message.answer('Невозможно обработать запрос')
    finally:
        data = await state.get_data()
        button_msg_id = data.get('button_message_id')
        if button_msg_id:
            await message.bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=button_msg_id,
                reply_markup=None
            )
        await state.clear()


@ai_router.callback_query(F.data == 'cancel_answer')
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Запрос отменен')

    await callback.message.edit_reply_markup(reply_markup=None)
    await state.clear()
