from evergy.evergy import Evergy

# Initialize the Evergy client with your credentials
evergy = Evergy("esburmeister", "ha)VZYP@gu12")

# Fetch and print the latest usage data
data = evergy.get_usage()
print("Today's kWh: " + str(data[-1]["usage"]))
print("Demand kWh: " + str(data[-1]["demand"]))
print("Period: " + str(data[-1]["period"]))
print("Cost: " + str(data[-1]["cost"]))
print("Bill Date: " + str(data[-1]["billDate"]))
print("Average Demand: " + str(data[-1]["avgDemand"]))
print("Average Temp: " + str(data[-1]["avgTemp"]))
print("Date: " + str(data[-1]["date"]))
print("Peak Demand: " + str(data[-1]["peakDemand"]))

