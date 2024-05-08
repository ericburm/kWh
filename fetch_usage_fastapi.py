from evergy.evergy import Evergy
import json

def fetch_usage():
    # Load credentials from the config file
    with open("config.json") as config_file:
        config = json.load(config_file)
        evergy_credentials = config["credentials"]

    # Initialize the Evergy client with your credentials
    evergy = Evergy(evergy_credentials["evergy_username"], evergy_credentials["evergy_password"])

    # Fetch the latest usage data
    data = evergy.get_usage()
    return data

