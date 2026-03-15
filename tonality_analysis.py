from transformers import pipeline
from aiogram import Router

from aiogram.filters import Command
from aiogram.types import Message

tonality_rt = Router()

classifier = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    device="cpu"
)

labels = ["positive", "neutral", "negative"]


def analyze_sentiment(text: str):
    result = classifier(
        text,
        candidate_labels=labels
    )

    best = result[0]

    return {
        "label": best["label"],
        "score": round(best["score"], 3)
    }


@tonality_rt.message(Command("sentiment"))
async def sentiment_handler(message: Message):

    text = message.text.replace("/sentiment ", "")

    result = analyze_sentiment(text)

    await message.answer(
        f"Тональность: {result['label']}\n"
        f"Уверенность: {result['score']}"
    )