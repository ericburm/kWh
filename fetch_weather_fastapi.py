import requests
import json
from datetime import datetime

def get_api_key():
    try:
        with open("config.json") as config_file:
            config = json.load(config_file)
            api_key = config.get("api_key")
            if api_key is None:
                raise ValueError("API key not found in the configuration file.")
            return api_key
    except FileNotFoundError:
        raise FileNotFoundError("Configuration file not found.")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in the configuration file.")

def fetch_weather(lat, lon):
    api_key = get_api_key()
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=en&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_report = {
            "Location": f"{data['name']}, {data['sys']['country']}",
            "Coordinates": data['coord'],
            "Weather Condition": data['weather'][0]['description'],
            "Temperature": data['main']['temp'],
            "Feels like": data['main']['feels_like'],
            "Min Temperature": data['main']['temp_min'],
            "Max Temperature": data['main']['temp_max'],
            "Pressure": data['main']['pressure'],
            "Humidity": data['main']['humidity'],
            "Visibility": data['visibility'],
            "Wind Speed": data['wind']['speed'],
            "Wind Direction": data['wind']['deg'],
            "Cloudiness": data['clouds']['all'],
            "Sunrise": datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S'),
            "Sunset": datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S'),
            "Date": datetime.now().strftime('%Y-%m-%d')
        }
        return weather_report
    else:
        return {"error": "Failed to fetch weather data"}

