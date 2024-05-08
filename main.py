from fastapi import FastAPI
import aiocron
from datetime import datetime
from fetch_usage_fastapi import fetch_usage
from fetch_weather_fastapi import fetch_weather

app = FastAPI()

# Global variables to store fetched data
usage_data = None
weather_data = None

@aiocron.crontab('0 12 * * *')  # Scheduled to run every day at 12:00 PM
async def scheduled_fetch_usage():
    global usage_data
    usage_data = await fetch_usage()
    print(f"Usage data fetched at {datetime.now()}")  # Logging the fetch time

@aiocron.crontab('5 12 * * *')  # Scheduled to run every day at 12:05 PM
async def scheduled_fetch_weather():
    global weather_data
    weather_data = await fetch_weather()
    print(f"Weather data fetched at {datetime.now()}")  # Logging the fetch time

@app.get("/usage")
async def get_usage():
    if usage_data is not None:
        return {"data": usage_data}
    else:
        return {"error": "Usage data not available. Please check back later."}

@app.get("/weather")
async def get_weather():
    if weather_data is not None:
        return {"data": weather_data}
    else:
        return {"error": "Weather data not available. Please check back later."}

