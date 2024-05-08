import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import requests
import csv
from datetime import datetime

def fetch_weather_and_email(lat, lon):
    api_key = "8a251e91ce924b26d0703c2fbd6b8d71"
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
        Date: {datetime.fromtimestamp(data['sys']['sunset']).strftime('%Y-%m-%d')}
        """
        csv_filename = save_to_csv(data)
        if csv_filename:
            send_email(csv_filename)
    else:
        print("Failed to fetch weather data")

def save_to_csv(data):
    csv_filename = "/home/burmlab/kWh/weather_report.csv"
    try:
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = ['Location', 'Coordinates', 'Weather Condition', 'Temperature', 'Feels like', 
                          'Min Temperature', 'Max Temperature', 'Pressure', 'Humidity', 'Visibility', 
                          'Wind Speed', 'Wind Direction', 'Cloudiness', 'Sunrise', 'Sunset', 'Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'Location': data['name'], 'Coordinates': data['coord'], 
                             'Weather Condition': data['weather'][0]['description'], 
                             'Temperature': data['main']['temp'], 'Feels like': data['main']['feels_like'], 
                             'Min Temperature': data['main']['temp_min'], 'Max Temperature': data['main']['temp_max'], 
                             'Pressure': data['main']['pressure'], 'Humidity': data['main']['humidity'], 
                             'Visibility': data['visibility'], 'Wind Speed': data['wind']['speed'], 
                             'Wind Direction': data['wind']['deg'], 'Cloudiness': data['clouds']['all'], 
                             'Sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S'), 
                             'Sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S'), 
                             'Date': datetime.fromtimestamp(data['sys']['sunset']).strftime('%Y-%m-%d')})
        return csv_filename
    except Exception as e:
        print(f"Failed to save to CSV: {e}")
        return None

def send_email(csv_filename):
    sender_email = "eric@burm.io"
    receiver_email = "esburmeister@gmail.com"
    subject = "Weather Report"
    body = "Please find attached the weather report CSV file."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    attachment = open(csv_filename, "rb")

    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % csv_filename.split('/')[-1])

    msg.attach(p)

    try:
        with smtplib.SMTP_SSL("mail.privateemail.com", 465) as server:
            server.login(sender_email, "LT2kk2gbnc")  # Replace with your account password
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Coordinates for Kansas City area
lat = 39.237864
lon = -94.664846

fetch_weather_and_email(lat, lon)

