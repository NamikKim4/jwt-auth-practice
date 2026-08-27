"""외부(Open-Meteo) 날씨 API에서 날씨를 가져와 PostgreSQL에 저장하는 백그라운드 작업.

Open-Meteo(https://open-meteo.com)는 회원가입도, API 키도, 신용카드 등록도 필요 없는
완전 무료 API라서 골랐어요. 절대 돈이 나갈 일이 없어요.

(저장소는 원래 MongoDB였는데, 나중에 게시글이랑 똑같이 PostgreSQL을 원본으로 두고
주기적으로 MongoDB에 백업하는 구조로 바꿨어요. weather_backup_sync.py가 그 백업을 맡아요.)
"""
import asyncio

import requests

from config import WEATHER_CITY_NAME, WEATHER_LAT, WEATHER_LON, WEATHER_FETCH_INTERVAL_SECONDS
from repositories.weather import create_auto_weather

# WMO 날씨 코드 → (한글 설명, 이모지). Open-Meteo가 숫자 코드로만 알려줘서 직접 매핑해요.
WEATHER_CODE_MAP = {
    0: ("맑음", "☀️"),
    1: ("대체로 맑음", "🌤️"),
    2: ("구름 조금", "⛅"),
    3: ("흐림", "☁️"),
    45: ("안개", "🌫️"),
    48: ("안개", "🌫️"),
    51: ("가벼운 이슬비", "🌦️"),
    53: ("이슬비", "🌦️"),
    55: ("강한 이슬비", "🌧️"),
    56: ("어는 이슬비", "🌧️"),
    57: ("강한 어는 이슬비", "🌧️"),
    61: ("가벼운 비", "🌧️"),
    63: ("비", "🌧️"),
    65: ("강한 비", "🌧️"),
    66: ("어는 비", "🌧️"),
    67: ("강한 어는 비", "🌧️"),
    71: ("가벼운 눈", "🌨️"),
    73: ("눈", "🌨️"),
    75: ("강한 눈", "❄️"),
    77: ("싸락눈", "🌨️"),
    80: ("소나기", "🌦️"),
    81: ("소나기", "🌧️"),
    82: ("강한 소나기", "⛈️"),
    85: ("가벼운 눈소나기", "🌨️"),
    86: ("강한 눈소나기", "🌨️"),
    95: ("뇌우", "⛈️"),
    96: ("뇌우(우박 동반)", "⛈️"),
    99: ("뇌우(강한 우박)", "⛈️"),
}


def describe_weather_code(code) -> tuple[str, str]:
    return WEATHER_CODE_MAP.get(code, ("정보 없음", "🌡️"))


def fetch_current_weather() -> dict:
    """Open-Meteo API를 호출해서 현재 날씨를 가져온다. API 키가 필요 없는 무료 API예요."""
    res = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": WEATHER_LAT,
            "longitude": WEATHER_LON,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "timezone": "Asia/Seoul",
        },
        timeout=10,
    )
    res.raise_for_status()
    current = res.json()["current"]

    description, emoji = describe_weather_code(current.get("weather_code"))

    return {
        "city": WEATHER_CITY_NAME,
        "temperature_c": current.get("temperature_2m"),
        "humidity_percent": current.get("relative_humidity_2m"),
        "wind_speed_ms": current.get("wind_speed_10m"),
        "description": description,
        "emoji": emoji,
    }


def fetch_and_store_weather():
    doc = fetch_current_weather()
    create_auto_weather(
        doc["city"], doc["temperature_c"], doc["humidity_percent"],
        doc["wind_speed_ms"], doc["description"], doc["emoji"],
    )
    print(f"[날씨] {doc['city']} {doc['temperature_c']}°C {doc['description']} — PostgreSQL에 저장 완료")


async def weather_background_loop():
    """서버가 켜져있는 동안 무한히 반복되는 백그라운드 작업.
    WEATHER_FETCH_INTERVAL_SECONDS(기본 30분)마다 한 번씩 날씨를 새로 가져와요.
    requests.get()은 동기(블로킹) 호출이라, asyncio.to_thread로 별도 스레드에서 돌려서
    메인 이벤트 루프(다른 API 요청들 처리하는 곳)를 막지 않게 했어요."""
    while True:
        try:
            await asyncio.to_thread(fetch_and_store_weather)
        except Exception as e:
            print(f"[날씨] 가져오기 실패 (다음 주기에 재시도): {e}")
        await asyncio.sleep(WEATHER_FETCH_INTERVAL_SECONDS)
