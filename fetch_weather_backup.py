import requests
import csv
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import json

def fetch_weather_and_send_email():
    try:
        with open("config.json") as config_file:
            config = json.load(config_file)
            api_key = config.get("api_key")
            receiver_email = config["credentials"]["receiver_email"]
            smtp_sender_email = config["credentials"]["smtp_sender_email"]
            smtp_sender_password = config["credentials"]["smtp_sender_password"]
            smtp_server = config["credentials"]["smtp_server"]
            smtp_port = config["credentials"]["smtp_port"]
            lat = config.get("coordinates", {}).get("lat")
            lon = config.get("coordinates", {}).get("lon")
            if None in (api_key, receiver_email, smtp_sender_email, smtp_sender_password, smtp_server, smtp_port, lat, lon):
                raise ValueError("Missing configuration in config.json.")
    except FileNotFoundError:
        raise FileNotFoundError("Configuration file not found.")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in the configuration file.")

    # Fetch weather data
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=en&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        csv_data = convert_to_csv(data)

        # Send email
        send_email(csv_data, receiver_email, smtp_sender_email, smtp_sender_password, smtp_server, smtp_port)
    else:
        print("Failed to fetch weather data.")

def convert_to_csv(data):
    fieldnames = ['Location', 'Coordinates', 'Weather Condition', 'Temperature (°C)', 'Feels like (°C)', 'Min Temperature (°C)', 'Max Temperature (°C)',
                  'Pressure (hPa)', 'Humidity (%)', 'Visibility (m)', 'Wind Speed (m/s)', 'Wind Direction (°)', 'Cloudiness (%)', 'Sunrise', 'Sunset', 'Date']
    csv_data = [fieldnames]
    csv_data.append([f"{data['name']}, {data['sys']['country']}", data['coord'], data['weather'][0]['description'],
                    data['main']['temp'], data['main']['feels_like'], data['main']['temp_min'], data['main']['temp_max'],
                    data['main']['pressure'], data['main']['humidity'], data['visibility'], data['wind']['speed'], data['wind']['deg'],
                    data['clouds']['all'], datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S'),
                    datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S'), datetime.fromtimestamp(data['sys']['sunset']).strftime('%Y-%m-%d')])
    return csv_data

def send_email(csv_data, receiver_email, smtp_sender_email, smtp_sender_password, smtp_server, smtp_port):
    msg = MIMEMultipart()
    msg['From'] = smtp_sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Weather Report"

    # Attach CSV file
    csv_filename = "weather_report.csv"
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)

    with open(csv_filename, 'rb') as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {csv_filename}")
    msg.attach(part)

    # Connect to SMTP server and send email
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_sender_email, smtp_sender_password)
            server.sendmail(smtp_sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    fetch_weather_and_send_email()

