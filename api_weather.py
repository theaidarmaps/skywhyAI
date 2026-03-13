import requests
import pandas as pd

def get_weather(lat: float, lon: float, days: int = 5):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "daily": ["temperature_2m_min", "temperature_2m_max", "precipitation_sum"],
        "forecast_days": days, "timezone": "Europe/Moscow"
    }
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        df = pd.DataFrame(resp.json()["daily"])
        return f"Погода на сегодня: {df['temperature_2m_min'][0]}–{df['temperature_2m_max'][0]}°C, осадки {df['precipitation_sum'][0]} мм"
    return "Ошибка получения погоды"