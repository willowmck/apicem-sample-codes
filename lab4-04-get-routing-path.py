import requests   # We use Python "requests" module to do HTTP GET query 
import json       # Import JSON encoder and decode module
from apicem_config import *    # APIC-EM IP is assigned in apicem_config.py
requests.packages.urllib3.disable_warnings()    # Remove this line if not using Python 3


# need to change source and destination IP to the one you like to trace
src = "40.0.0.14"
dest = "40.0.0.15"
url = "https://"+apicem_ip+"/api/v0/routing-path/"+src+"/"+dest

r = requests.get(url,verify=False)
response_json = r.json()
print ("Status: ",r.status_code)
print (json.dumps(response_json,indent=4))
print ("If you don't see the destination host shows up in node section that means there is no route from src to dest")
