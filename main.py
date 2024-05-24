import requests
import psycopg2
import json
from datetime import datetime

# Load configuration from config.json
with open('/home/burmlab/kWh/config.json') as config_file:
    config = json.load(config_file)

# Database connection details
db_host = "127.0.0.1"
db_name = config["credentials"]["postgres_db"]
db_user = config["credentials"]["postgres_user"]
db_pass = config["credentials"]["postgres_password"]

# API endpoints
usage_url = "http://127.0.0.1:8080/usage"
weather_url = "http://127.0.0.1:8080/weather"

def fetch_data(url):
    response = requests.get(url)
    return response.json()

def store_data_in_db(usage_data, weather_data):
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_pass,
            host=db_host
        )
        cursor = conn.cursor()

        # Create usage table if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id SERIAL PRIMARY KEY,
            period VARCHAR(50),
            bill_start TIMESTAMP,
            bill_end TIMESTAMP,
            bill_date TIMESTAMP,
            date DATE,
            usage FLOAT,
            demand FLOAT,
            avg_demand FLOAT,
            peak_demand FLOAT,
            peak_date_time VARCHAR(50),
            max_temp FLOAT,
            min_temp FLOAT,
            avg_temp FLOAT,
            cost FLOAT,
            balance FLOAT,
            is_partial BOOLEAN
        );
        """)

        # Create weather table if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id SERIAL PRIMARY KEY,
            lon FLOAT,
            lat FLOAT,
            main VARCHAR(50),
            description VARCHAR(100),
            temp FLOAT,
            feels_like FLOAT,
            temp_min FLOAT,
            temp_max FLOAT,
            pressure INT,
            humidity INT,
            visibility INT,
            wind_speed FLOAT,
            wind_deg INT,
            clouds_all INT,
            dt TIMESTAMP,
            sunrise TIMESTAMP,
            sunset TIMESTAMP,
            name VARCHAR(50)
        );
        """)

        # Insert usage data
        cursor.execute("""
        INSERT INTO usage (period, bill_start, bill_end, bill_date, date, usage, demand, avg_demand, peak_demand, peak_date_time, max_temp, min_temp, avg_temp, cost, balance, is_partial)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            usage_data["latest"]["period"],
            datetime.fromisoformat(usage_data["latest"]["billStart"]),
            datetime.fromisoformat(usage_data["latest"]["billEnd"]),
            datetime.fromisoformat(usage_data["latest"]["billDate"]),
            datetime.strptime(usage_data["latest"]["date"], '%m/%d/%Y').date(),
            usage_data["latest"]["usage"],
            usage_data["latest"]["demand"],
            usage_data["latest"]["avgDemand"],
            usage_data["latest"]["peakDemand"],
            usage_data["latest"]["peakDateTime"],
            usage_data["latest"]["maxTemp"],
            usage_data["latest"]["minTemp"],
            usage_data["latest"]["avgTemp"],
            usage_data["latest"]["cost"],
            usage_data["latest"]["balance"],
            usage_data["latest"]["isPartial"]
        ))

        # Insert weather data
        cursor.execute("""
        INSERT INTO weather (lon, lat, main, description, temp, feels_like, temp_min, temp_max, pressure, humidity, visibility, wind_speed, wind_deg, clouds_all, dt, sunrise, sunset, name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            weather_data["coord"]["lon"],
            weather_data["coord"]["lat"],
            weather_data["weather"][0]["main"],
            weather_data["weather"][0]["description"],
            weather_data["main"]["temp"],
            weather_data["main"]["feels_like"],
            weather_data["main"]["temp_min"],
            weather_data["main"]["temp_max"],
            weather_data["main"]["pressure"],
            weather_data["main"]["humidity"],
            weather_data["visibility"],
            weather_data["wind"]["speed"],
            weather_data["wind"]["deg"],
            weather_data["clouds"]["all"],
            datetime.fromtimestamp(weather_data["dt"]),
            datetime.fromtimestamp(weather_data["sys"]["sunrise"]),
            datetime.fromtimestamp(weather_data["sys"]["sunset"]),
            weather_data["name"]
        ))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

def main():
    usage_data = fetch_data(usage_url)
    weather_data = fetch_data(weather_url)
    store_data_in_db(usage_data, weather_data)

if __name__ == "__main__":
    main()

