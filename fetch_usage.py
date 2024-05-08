import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import csv
from evergy.evergy import Evergy
import json
import os

def fetch_usage_and_email():
    # Load credentials from the config file
    with open('config.json') as f:
        config = json.load(f)
        evergy_credentials = config["credentials"]

    # Initialize the Evergy client with your credentials
    evergy = Evergy(evergy_credentials["evergy_username"], evergy_credentials["evergy_password"])

    # Fetch the latest usage data
    data = evergy.get_usage()

    csv_filename = save_to_csv(data)
    if csv_filename:
        send_email(csv_filename, evergy_credentials)

def save_to_csv(data):
    current_directory = os.getcwd()
    csv_filename = os.path.join(current_directory, 'usage_report.csv')
    try:
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Usage (kWh)', 'Demand (kWh)', 'Period', 'Cost', 'Bill Date', 
                          'Average Demand', 'Average Temp', 'Peak Demand']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'Date': data[-1]["date"], 'Usage (kWh)': data[-1]["usage"], 
                             'Demand (kWh)': data[-1]["demand"], 'Period': data[-1]["period"], 
                             'Cost': data[-1]["cost"], 'Bill Date': data[-1]["billDate"], 
                             'Average Demand': data[-1]["avgDemand"], 'Average Temp': data[-1]["avgTemp"], 
                             'Peak Demand': data[-1]["peakDemand"]})
        return csv_filename
    except Exception as e:
        print(f"Failed to save to CSV: {e}")
        return None

def send_email(csv_filename, credentials):
    sender_email = credentials["smtp_sender_email"]
    receiver_email = credentials["receiver_email"]
    subject = "Usage Report"
    body = "Please find attached the usage report CSV file."

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
        with smtplib.SMTP_SSL(credentials["smtp_server"], credentials["smtp_port"]) as server:
            server.login(sender_email, credentials["smtp_sender_password"])
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

fetch_usage_and_email()

