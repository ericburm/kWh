from fastapi import FastAPI, HTTPException, Request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import requests
import json
import os
from evergy.evergy import Evergy

# Load configuration
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.json")

if not os.path.exists(config_path):
    raise FileNotFoundError(f"Configuration file not found: {config_path}")

with open(config_path, "r") as f:
    config = json.load(f)

API_KEY = config["api_key"]
EVERGY_USERNAME = config["credentials"]["evergy_username"]
EVERGY_PASSWORD = config["credentials"]["evergy_password"]
LAT = config["coordinates"]["lat"]
LON = config["coordinates"]["lon"]

app = FastAPI()
scheduler = BackgroundScheduler()

# In-memory storage
weather_data = {}
usage_data = {}

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Application"}

@app.get("/weather")
def get_weather():
    fetch_weather_job()  # Fetches fresh data
    if not weather_data:
        raise HTTPException(status_code=404, detail="No weather data available")
    return weather_data

@app.post("/weather")
async def post_weather(request: Request):
    new_weather = await request.json()
    weather_data.update(new_weather)
    return weather_data

@app.get("/usage")
def get_usage():
    fetch_usage_job()  # Fetches fresh data
    if not usage_data:
        raise HTTPException(status_code=404, detail="No usage data available")
    return usage_data

@app.post("/usage")
async def post_usage(request: Request):
    new_usage = await request.json()
    usage_data.update(new_usage)
    return usage_data

@app.on_event("startup")
def startup_event():
    scheduler.add_job(func=fetch_weather_job, trigger=CronTrigger(hour=12, minute=0))
    scheduler.add_job(func=fetch_usage_job, trigger=CronTrigger(hour=22, minute=0))
    scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

def fetch_weather_job():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&units=metric&lang=en&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        weather_data.update(response.json())
        print("Weather data fetched:", weather_data)
    else:
        print(f"Error fetching weather data: {response.status_code}")

def fetch_usage_job():
    evergy = Evergy(EVERGY_USERNAME, EVERGY_PASSWORD)
    data = evergy.get_usage()
    if isinstance(data, list) and data:
        usage_data.update({"latest": data[-1]})
        print("Usage data fetched:", usage_data)
    else:
        print("Error fetching usage data.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

