import requests
from geopy.geocoders import Nominatim
from aiogram import Router

from aiogram.filters import Command
from aiogram.types import Message

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

rt = Router()

def get_weather(lat: float, lon: float, days: int = 5) -> str:
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_min",
            "temperature_2m_max",
            "precipitation_sum"
        ],
        "forecast_days": days,
        "timezone": "auto"
    }

    resp = requests.get(url, params=params)

    if resp.status_code != 200:
        return "❌ Ошибка получения погоды"

    data = resp.json()["daily"]

    text = "🌤 <b>Прогноз погоды</b>\n\n"

    for i in range(days):
        date = data["time"][i]
        t_min = data["temperature_2m_min"][i]
        t_max = data["temperature_2m_max"][i]
        rain = data["precipitation_sum"][i]

        text += (
            f"📅 {date}\n"
            f"🌡 {t_min}°C – {t_max}°C\n"
            f"🌧 Осадки: {rain} мм\n\n"
        )

    return text

geolocator = Nominatim(user_agent="weather_bot")

class WeatherState(StatesGroup):
    waiting_for_city = State()

@rt.message(Command("weather"))
async def weather_command(message: Message, state: FSMContext):
    await message.answer("Напиши город 🌍")
    await state.set_state(WeatherState.waiting_for_city)

@rt.message(WeatherState.waiting_for_city)
async def get_city(message: Message, state: FSMContext):
    city = message.text

    location = geolocator.geocode(city)

    if location is None:
        await message.answer("Город не найден ❌ Попробуй еще раз")
        return

    lat = location.latitude
    lon = location.longitude

    weather = get_weather(lat, lon)

    await message.answer(f"Погода в городе <b>{city}</b>\n\n{weather}")

    await state.clear()
