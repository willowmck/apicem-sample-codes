import requests
import json
import sys
from apicem_config import * # APIC-EM IP is assigned in apicem_config.py

# remove this line if not using Python 3                                     
requests.packages.urllib3.disable_warnings()
device_ip = "40.0.1.6"
# Prepare network device list
url = "https://"+apicem_ip+"/api/v0/network-device/count"   # API base url
resp= requests.get(url,verify=False)     # The response (result) from "GET /network-device/count" query
response_json = resp.json() # Get the json-encoded content from response with "response_json = resp.json()
count = response_json["response"]    # Total count of network-device and convert it to string

if count > 0 :
    device_list = []
    url = "https://"+apicem_ip+"/api/v0/network-device/1/"+str(count)  # API base url, convert 'count' to string
    resp= requests.get(url,verify=False) # The response (result) from "GET /network-device/{startIndex}/{recordsToReturn}" query
    response_json = resp.json() # Get the json-encoded content from response
    for item in response_json["response"]:
        device_list.append([item["hostname"],item["type"],item["managementIpAddress"],item["id"]])
    device_list.sort()
else:
    print ("No network device found !")
    sys.exit(1)

# find out network device id for network device with IP
if device_ip != "":
    id = ""
    for item in device_list:
        if item[2] == device_ip:
            id = item[3]   
    # index 2 is for IP and index 3 is for id
    # get IOS configuration for  network device with IP 10.10.40.253
    if id != "":
        url =  "https://"+apicem_ip+"/api/v0/network-device/"+id+"/config"
        resp= requests.get(url,verify=False)
        response_json = resp.json()
        # replace "\r\n" to "\n" to remove extra space live (Carriage Return)
        print (response_json["response"].replace("\r\n","\n"))
    else:
        print("No device was found for IP " + device_ip)       
else:
    print("IP address was not specified.  Please add IP address.")
