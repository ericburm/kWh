from evergy.evergy import Evergy

def fetch_usage():
    # Initialize the Evergy client with your credentials
    evergy = Evergy("esburmeister", "ha)VZYP@gu12")  # Be cautious with credentials

    # Fetch the latest usage data
    data = evergy.get_usage()
    return data

