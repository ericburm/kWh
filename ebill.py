import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import os
import psycopg2

# Get the current working directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Load credentials from config.json
config_path = os.path.join(current_directory, 'config.json')
with open(config_path) as config_file:
    config = json.load(config_file)

evergy_username = config['credentials']['evergy_username']
evergy_password = config['credentials']['evergy_password']
smtp_sender_email = config['credentials']['smtp_sender_email']
smtp_sender_password = config['credentials']['smtp_sender_password']
smtp_server = config['credentials']['smtp_server']
smtp_port = config['credentials']['smtp_port']
receiver_email = config['credentials']['receiver_email']
postgres_user = config['credentials']['postgres_user']
postgres_password = config['credentials']['postgres_password']
postgres_db = config['credentials']['postgres_db']
postgres_host = config['credentials']['postgres_host']
postgres_port = config['credentials']['postgres_port']

# Connect to the PostgreSQL database and fetch the last eBill URL
conn = psycopg2.connect(
    dbname=postgres_db, 
    user=postgres_user, 
    password=postgres_password, 
    host=postgres_host, 
    port=postgres_port
)
cur = conn.cursor()
cur.execute("SELECT link FROM links ORDER BY id DESC LIMIT 1;")
ebill_url = cur.fetchone()[0]
cur.close()
conn.close()

# Session to persist login
session = requests.Session()

# URL for Evergy login
login_url = 'https://www.evergy.com/log-in'

def login():
    # Fetch the login form to get the CSRF token
    login_form = session.get(login_url)
    login_form_soup = BeautifulSoup(login_form.text, 'html.parser')
    
    # Extract the CSRF token and its name
    csrf_token = login_form_soup.select('.login-form > input')[0]['value']
    csrf_token_name = login_form_soup.select('.login-form > input')[0]['name']
    
    # Prepare the login payload with the CSRF token
    login_payload = {
        'Username': evergy_username,
        'Password': evergy_password,
        csrf_token_name: csrf_token,
    }
    
    # Send a POST request to log in
    response = session.post(url=login_url, data=login_payload, allow_redirects=False)
    response.raise_for_status()
    print("Logged in successfully")

# Perform login
login()

# Download the eBill PDF
pdf_response = session.get(ebill_url)
pdf_response.raise_for_status()

# Save the PDF to a variable
pdf_data = pdf_response.content

# Email the PDF
msg = MIMEMultipart()
msg['From'] = smtp_sender_email
msg['To'] = receiver_email
msg['Subject'] = 'Monthly Evergy Bill'

body = 'Attached is your monthly Evergy bill.'
msg.attach(MIMEText(body, 'plain'))

# Attach the PDF
attachment = MIMEApplication(pdf_data, _subtype="pdf")
attachment.add_header('Content-Disposition', 'attachment', filename='Evergy_Bill.pdf')
msg.attach(attachment)

# Send the email
with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
    server.login(smtp_sender_email, smtp_sender_password)
    server.sendmail(smtp_sender_email, receiver_email, msg.as_string())

print('Email sent successfully.')

