import os
import requests
import json
import sys
import random
import time

#get the os token of openstack
base_url = "http://localhost"
token_url = base_url + "/identity/v3/auth/tokens"
headers = {'Contenet-Type': 'application/json'}
data = {
   "auth":{
      "identity":{
         "methods":[
            "password"
         ],
         "password":{
            "user":{
               "name":"admin",
               "domain":{
                  "id":"default"
               },
               "password":"secret"
            }
         }
      },
      "scope":{
         "project":{
            "name":"admin",
            "domain":{
               "id":"default"
            }
         }
      }
   }
}

resp = requests.post(token_url, headers=headers, data=json.dumps(data))
resp_header_dict = dict(resp.headers)
os_token = resp_header_dict['X-Subject-Token']
print("os_token: " + os_token)

#get the project id of admin
project_url = base_url + "/identity/v3/projects"
headers = {'X-Auth-Token': os_token}
resp = requests.get(project_url, headers=headers)
resp_json = resp.json()
for x in resp_json['projects']:
    if x['name'] == "admin":
        project_id = x['id']
print("proejct_id: " + project_id)

#get one of the network id of admin project
network_url = base_url + ":9696/v2.0/networks"
headers = {'X-Auth-Token': os_token}
resp = requests.get(network_url, headers=headers)
resp_json = resp.json()
for i, x in enumerate(resp_json['networks']):
    if x['project_id'] == project_id:
        network_id = x['id']
        break
    if i == len(resp_json['networks'])-1:
        print("no network found in admin project, please create one for creating vm")
        sys.exit(1)
print("network_id: " +network_id)

#get the image id
image_url = base_url + "/image/v2/images"
resp=requests.get(image_url, headers=headers)
resp_json = resp.json()
for x in resp_json['images']:
    if x['name'] == "cirros-0.3.5-x86_64-disk":
        image_id = x['id']
        break
print("image_id: " + image_id)

################################################################################
#This function is to collect the data from devstack VM
#This include CPU utilization, frequency, and memory usage
################################################################################
def collect():
    stdout = os.popen('mpstat -P ALL').read()
    for i, x in enumerate(stdout.split('\n')):
        if i == 3:
            y = x.split()
            #print out the time
            print("Time: " + y[0] + y[1])
            print("CPU Utilization")
        if i > 3:
            #list all the cpu usage usr + sys
            y = x.split()
            if len(y) == 0:
                break
            utilisation = float(y[3]) + float(y[5])
            print("CPU" + y[2] + ": " + str(utilisation))
    
    stdout =  os.popen('cat /proc/cpuinfo | grep MHz').read()
    print("CPU Frequency MHz")
    #list all the cpu frequency
    for i, x in enumerate(stdout.split('\n')):
        y = x.split()
        if len(y) == 0:
            break
        print("CPU" + str(i) + ": " + y[3])

    #list the memory usage
    stdout =  os.popen('free -m').read()
    for i, x in enumerate(stdout.split('\n')):
        if i == 1:
            y = x.split()
            print("Memory Usage: " + y[2] + "/" + y[1])

################################################################################
#Create a random number of VMs
################################################################################
def create():
    global base_url, os_token, resp, resp_json, project_id, network_id, image_id
    server_url = base_url + "/compute/v2.1/servers"
    headers = {'X-Auth-Token': os_token, 'Contenet-Type': 'application/json'}
    #create random number of vm between 1 to 4
    num_vm_create = random.randint(1,4)
    print("creating " + str(num_vm_create) + " VM")
    for i in range(num_vm_create):
        vm_name = "vm" + str(i)
        data = {
        "server":{
            "flavorRef":"42",
            "name": vm_name,
            "networks":[
                {
                    "uuid": network_id
                }
            ],
            "imageRef": image_id
        }
        }
        resp = requests.post(server_url, headers=headers, data = json.dumps(data))

################################################################################
#Delete all the VM inside openstack
################################################################################
def delete():
    print("clear all the VM")
    global base_url, os_token, resp, resp_json, project_id
    server_url = base_url + "/compute/v2.1/servers"
    headers = {'X-Auth-Token': os_token}
    resp = requests.get(server_url, headers=headers)
    resp_json = resp.json()
    server_list = []
    #get all the server id
    for x in resp_json['servers']:
        server_list.append(x['id'])
    for i in range(len(server_list)):
        delete_server_url = server_url + "/" + server_list[i]
        resp = requests.delete(delete_server_url, headers=headers)

################################################################################
#change the activate/disable a CPU core
################################################################################
def change(core_index,enable):
    if core_index == 0:
        print("could not change the status of cpu 0")
        return
    if core_index > 3:
        print("the index of cpu out of range")
        return
    #enalbe that cpu core
    if enable == True :
        string = "sudo sh -c \"echo -n 1 > /sys/devices/system/cpu/cpu" + str(core_index) + "/online\""
        os.system(string)
    #disable that cpu core
    elif enable == False:
        string = "sudo sh -c \"echo -n 0 > /sys/devices/system/cpu/cpu" + str(core_index) + "/online\""
        os.system(string)

################################################################################
#This function only collect the average (all with cmd mpstat) cpu utilization
################################################################################
def collect_average():
    stdout = os.popen('mpstat -P ALL').read()
    for i, x in enumerate(stdout.split('\n')):
        if i == 3:
            y = x.split()
            utilisation = float(y[3]) + float(y[5])
            print("Time: " + y[0] + y[1] + ", " +"CPU: " + str(utilisation))

if __name__ == "__main__":
    for i in range(16):
        delete()
        create()
        collect_average()
        time.sleep(60)
    delete()