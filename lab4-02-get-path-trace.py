from apicem_config import * # apicem_config.py is the central place to change the apic-em IP, username, password ...etc
import time # Need it for delay - sleep() function

# Get token - function is in apicem_config.py
ticket = get_X_auth_token()
headers = {"content-type" : "application/json","X-Auth-Token": ticket}
base_url = "https://"+apicem_ip+"/api/"+version  # API base url
host_ip_list=[]
device_ip_list=[]

def getItemsFromUrl(command, list, itemName):
    try:
        resp = requests.get(base_url + command, headers=headers, verify = False)
        print ('Status of GET ' + base_url + command + ': ', resp.status_code)
        response_json = resp.json()
        for item in response_json["response"]:
            list.append(item[itemName])
    except:
        print ("Something went wrong, cannot get " + itemName + "!")

def printItems(list, description):
    print("\n-----------" + description + "----------")
    if list == [] :
        print("\n       There is no " + description)
    else:
        for item in list:
            print('\t', item)

def verify_hosts_and_devices():
    if host_ip_list== [] and device_ip_list == []:
        print ("There is no any host or network device !!!")
        sys.exit()

def selectIp(direction):
    select = True
    while select:
        s_ip = input('=> Please select a ' + direction +
            ' ip address from above list: ')
        s_ip = s_ip.replace(" ","")
        if s_ip in host_ip_list or s_ip in device_ip_list:
            return s_ip
        else:
            print ("IP address you entered is NOT on the list !")

def printJSONResponse(info, response_json):
    print(info, json.dumps(response_json, indent=4))

def getFlowAnalysis(source, destination):
    path_data = {"sourceIP": source, "destIP": destination}
    r = requests.post(base_url+"/flow-analysis", json.dumps(path_data),
        headers=headers,verify=False)
    response_json = r.json()
    print ("\nPOST flow-analysis Status: ",r.status_code)
    printJSONResponse("Response from POST /flow-analysis:\n", response_json)
    return response_json

def getTaskId(response_json):
    try:
        return response_json["response"]["taskId"]
    except:
        print("\n For some reason cannot get taskId")
        sys.exit()

def getTask(response_json, taskId):
    url = "https://"+apicem_ip+"/api/"+version+"/task/"+taskId
    r = requests.get(url, headers=headers, verify=False)
    response_json = r.json()
    print ("\nGET task with taskId status: ", r.status_code)
    printJSONResponse("Response from GET /task/taskId:\n", response_json)
    return response_json

def getPath(response_json):
    # endTime exist,can get pathId now
    # pathId is the value of "progress" attribute
    if response_json["response"]["isError"] == "true":
        print ("\nSomething not right, here is the response:\n")
        printJSONResponse(
            "\n*** Response from GET /flow-analysis/pathId.- Trace path " +
            "information. ***\n", response_json)
    else:
        pathId = response_json["response"]["progress"]
        print ("\nPOST flow-analysis task is finished now, here is the pathId: ",
            pathId)
        url = base_url+"/flow-analysis/"+pathId
        r = requests.get(url,headers=headers,verify=False)
        response_json = r.json()
        print ("\nGET /flow-analysis/pathId Status: ",r.status_code)
        printJSONResponse(
            "\n*** Response from GET /flow-analysis/pathId.- Trace path " +
            "information. ***\n", response_json)
        return pathId

def getPathBlocking(response_json,taskId):
    pathId = ""
    while pathId =="":
        try:
            response_json["response"]["endTime"]
        except:
            # No endTime, no pathId yet
            print ("\nTask is not finished yet, sleep 1 second then try again")
            time.sleep(1)
            response_json = getTask(response_json, taskId)
        else:
            pathId = getPath(response_json)

# Main program - Show hosts and network devices
# The user should choose a source and destination
getItemsFromUrl("/host", host_ip_list, 'hostIp')
getItemsFromUrl("/network-device", device_ip_list, 'managementIpAddress')
printItems(host_ip_list, 'host')
printItems(device_ip_list, 'network-device')
verify_hosts_and_devices()

print ("*** Please note that not all source/destination ip pair will return a " +
    "path - no route. ! *** \n")

# Use Flow Analysis on the source and destination
# Then use a blocking call to get the full path information and print to stdout
source_ip = selectIp('source')
destination_ip = selectIp('destination')
response_json = getFlowAnalysis(source_ip, destination_ip)
taskId = getTaskId(response_json)
response_json = getTask(response_json, taskId)
getPathBlocking(response_json, taskId)
