import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import os

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

# Session to persist login
session = requests.Session()

# URL for Evergy login and eBill
login_url = 'https://www.evergy.com/log-in'
ebill_url = 'https://www.evergy.com/api/document/ebill?payload=71CA44BB28417BD5400761D0A47FB551/6D7FF905A0735994DF0C3665608F6D5468FA20ADAB66076B39F5CA8636870DD86DC2E8E1A8B36A1AB61E0105012683690FC21B02D4C6B2F62BD3C61990A77025C387FB6BA8852CC0F8D3ABD88BFB7E4B6D327E991DB78D281FA378B4BF5C4B77FC8C113F314FC4EFCC192B2B229702E1D046C3ECDC52A09BD15C4496D647497A'

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

