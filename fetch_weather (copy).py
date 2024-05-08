import requests
from datetime import datetime  # Import the datetime class from the datetime module

def fetch_weather(lat, lon):
    api_key = "8a251e91ce924b26d0703c2fbd6b8d71"  # Your API key
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=en&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200:
        print("Weather data retrieved successfully:")
        print("Location:", data['name'], data['sys']['country'])
        print("Coordinates:", data['coord'])
        print("Weather Condition:", data['weather'][0]['description'])
        print("Temperature: {} °C".format(data['main']['temp']))
        print("Feels like: {} °C".format(data['main']['feels_like']))
        print("Min Temperature: {} °C".format(data['main']['temp_min']))
        print("Max Temperature: {} °C".format(data['main']['temp_max']))
        print("Pressure:", data['main']['pressure'], "hPa")
        print("Humidity:", data['main']['humidity'], "%")
        print("Visibility:", data['visibility'], "meters")
        print("Wind Speed:", data['wind']['speed'], "meter/sec")
        print("Wind Direction:", data['wind']['deg'], "degrees")
        print("Cloudiness:", data['clouds']['all'], "%")
        print("Sunrise:", datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S'))
        print("Sunset:", datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S'))
        print("Date:", datetime.fromtimestamp(data['sys']['sunset']).strftime('%Y-%m-%d'))
    else:
        print("Failed to fetch weather data")

# Coordinates for Kansas City area
lat = 39.237864
lon = -94.664846

fetch_weather(lat, lon)

