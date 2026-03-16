import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from transliterate import translit
from transformers import pipeline

tonality_rt = Router()

tiny_classifier = pipeline(
    'text-classification',
    model='cointegrated/rubert-tiny-toxicity',
)


@tonality_rt.message(Command('sentiment'))
async def sentiment_handler(message: Message):
    text = message.text.replace('/sentiment', '').strip()
    if not text:
        await message.answer('После /sentiment текст')
        return

    orig = text
    lower_text = text.lower()
    if re.search(r'[a-zA-Z]', text) and not re.search(r'[а-яА-ЯёЁ]', text):
        try:
            text = translit(text, 'ru', reversed=True)
            lower_text = text.lower()
        except Exception:
            text = orig
            lower_text = orig.lower()

    tiny_results = tiny_classifier(text)
    tiny_top = max(tiny_results, key=lambda x: x['score'])
    tiny_score = round(tiny_top['score'], 3)

    tiny_mapping = {
        'non-toxic':  ('✅', 'Норм'),
        'insult':     ('🤬', 'Оскорбление'),
        'obscenity':  ('💩', 'Мат'),
        'threat':     ('⚠️', 'Угроза'),
        'dangerous':  ('🚨', 'Опасно'),
        'toxic':      ('😈', 'Токсик')
    }
    tiny_emoji, tiny_verdict = tiny_mapping.get(tiny_top['label'], ('❓', tiny_top['label']))

    emoji = tiny_emoji
    verdict = tiny_verdict
    score = tiny_score

    # Короткий вывод с цитатой
    quoted = text[:50] + '...' if len(text) > 50 else text
    reply = f'<i>{quoted}</i>\n{emoji} {verdict} {score:.2f}'

    await message.answer(reply, parse_mode='HTML')
