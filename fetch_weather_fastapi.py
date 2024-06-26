import json
import requests
import logging

# Configure logging
logging.basicConfig(filename='weather.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_api_key():
    try:
        with open("config.json") as config_file:
            config = json.load(config_file)
            api_key = config.get("api_key")
            if not api_key:
                raise ValueError("API key not found in the configuration file.")
            return api_key
    except FileNotFoundError as e:
        logging.error("Configuration file not found: %s", e)
        raise e
    except json.JSONDecodeError as e:
        logging.error("Invalid JSON format in the configuration file: %s", e)
        raise ValueError("Invalid JSON format in the configuration file.")

def fetch_weather(lat, lon):
    try:
        api_key = get_api_key()
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=en&appid={api_key}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP status codes >= 400
        data = response.json()
        return data
    except requests.RequestException as e:
        logging.error("Failed to fetch weather data: %s", e)
        return {"error": f"Failed to fetch weather data: {e}"}
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        return {"error": f"An unexpected error occurred: {e}"}

def send_weather_data(lat, lon):
    try:
        weather_data = fetch_weather(lat, lon)
        url = "http://localhost:8080/weather"  # Adjust URL if necessary
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=weather_data, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP status codes >= 400
        logging.info("Weather data sent successfully")
    except requests.RequestException as e:
        logging.error("Failed to send weather data: %s", e)
    except Exception as e:
        logging.error("An unexpected error occurred while sending weather data: %s", e)

if __name__ == "__main__":
    # Example usage
    latitude = 51.51  # Example latitude
    longitude = -0.13  # Example longitude
    send_weather_data(latitude, longitude)

