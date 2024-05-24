from fastapi import FastAPI, HTTPException
from evergy.evergy import Evergy
import json
import requests

app = FastAPI()

# Load configurations from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Initialize the Evergy client with your credentials
evergy = Evergy(config["credentials"]["evergy_username"], config["credentials"]["evergy_password"])

# Fetch the latest usage data
data = evergy.get_usage()
latest_data = data[-1]

# Define the endpoint URL
endpoint_url = "http://localhost:8080/usage"

# Prepare the payload
payload = {
    "today_kWh": latest_data["usage"],
    "demand_kWh": latest_data["demand"],
    "period": latest_data["period"],
    "cost": latest_data["cost"],
    "bill_date": latest_data["billDate"],
    "average_demand": latest_data["avgDemand"],
    "average_temp": latest_data["avgTemp"],
    "date": latest_data["date"],
    "peak_demand": latest_data["peakDemand"]
}

# Post the data to the endpoint
try:
    response = requests.post(endpoint_url, json=payload)
    response.raise_for_status()
    print("Data successfully posted to the endpoint.")
except requests.exceptions.RequestException as e:
    print(f"Error posting data to the endpoint: {e}")

