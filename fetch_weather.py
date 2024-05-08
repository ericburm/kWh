import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import requests
import csv
from datetime import datetime
import json

def fetch_weather_and_email(lat, lon):
    try:
        with open("config.json") as config_file:
            config = json.load(config_file)
            api_key = config.get("api_key")
            if api_key is None:
                raise ValueError("API key not found in the configuration file.")
    except FileNotFoundError:
        raise FileNotFoundError("Configuration file not found.")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in the configuration file.")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=en&appid={api_key}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        weather_report = f"""
        Weather data retrieved successfully:
        Location: {data['name']}, {data['sys']['country']}
        Coordinates: {data['coord']}
        Weather Condition: {data['weather'][0]['description']}
        Temperature: {data['main']['temp']} °C
        Feels like: {data['main']['feels_like']} °C
        Min Temperature: {data['main']['temp_min']} °C
        Max Temperature: {data['main']['temp_max']} °C
        Pressure: {data['main']['pressure']} hPa
        Humidity: {data['main']['humidity']} %
        Visibility: {data['visibility']} meters
        Wind Speed: {data['wind']['speed']} meter/sec
        Wind Direction: {data['wind']['deg']} degrees
        Cloudiness: {data['clouds']['all']} %
        Sunrise: {datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S')}
        Sunset: {datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S')}
        Date: {datetime.fromtimestamp(data

