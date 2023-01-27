import requests
import json
import time
import sys

base_url = "http://localhost:8181/onos/v1/"

#example of a flow in json format
flow_json_example = '''{
  "priority": 40001,
  "timeout": 0,
  "isPermanent": true,
  "deviceId": "of:0000000000000001",
  "treatment": {
    "instructions": [
      {
        "type": "OUTPUT",
        "port": "1"
      }
    ]
  },
  "selector": {
    "criteria": [      
      {
        "type": "IN_PORT",
        "port": "2"
      }
    ]
  }
}'''

# get all hosts id
def get_hosts():
	url = base_url + "hosts"
	handler = requests.get(url, auth=('onos','rocks'))
	hosts_json = handler.json()
	host_id = []
	for i in hosts_json['hosts']:
		host_id.append(str(i['id']))
	return host_id

# get all connection switches id and port of the host
def get_host_connection(host_id):
	url = base_url + "hosts/" + host_id
	handler = requests.get(url, auth=('onos','rocks'))
	host_json = handler.json()
	host_con = []
	for i in host_json['locations']:
		host_con.append([str(i['elementId']),str(i['port'])])
	return host_con

#get all switches id
def get_devices():
	url = base_url + "devices"
	handler = requests.get(url, auth=('onos','rocks'))
	devices_json = handler.json()
	device_id = []
	for i in devices_json['devices']:
		device_id.append(str(i['id']))
	return device_id

#use onos short path api to find the path
def get_path(s1,s2):
	url = base_url + "paths/" + s1 + "/" + s2
	handler = requests.get(url, auth=('onos','rocks'))
	paths_json = handler.json()
	path = []
	for i in paths_json['paths'][0]['links']:
		path.append([str(i['src']['device']),str(i['src']['port'])])
		path.append([str(i['dst']['device']),str(i['dst']['port'])])
	return path

#setup the flow
def setup_flow(h1,h2):
        print("seting up the flow entires ...............")
	path_list = []
	for h in (h1,h2):
		tmp = get_host_connection(h)
		path_list.append([tmp[0][0],tmp[0][1]])
	tmp = get_path(path_list[0][0],path_list[1][0])
	for i in range (len(tmp)):
		path_list.append([tmp[i][0],tmp[i][1]])
	tmp = path_list[1]

	#arrange the path in order from h1 to h2
	for i in range(2,len(path_list)):
		path_list[i-1] = path_list[i]
	path_list[len(path_list)-1] = tmp

        headers = {'content-Type':'application/json'}
        data = flow_rule_gen(path_list[0][0],path_list[0][1],path_list[1][1])
        for i in range(0,len(path_list),2):
                url = base_url + "flows/" + path_list[i][0]
                data = flow_rule_gen(path_list[i][0],path_list[i][1],path_list[i+1][1])
                response = requests.post(url,auth=('onos','rocks'),data=data,headers=headers)
                data = flow_rule_gen(path_list[i][0],path_list[i+1][1],path_list[i][1])
                response = requests.post(url,auth=('onos','rocks'),data=data,headers=headers)
                print("setup the flow entries: " + path_list[i][0])
        return path_list

#remove all the flow with appId "org.onosproject.rest"
def remove_all_flows():
        device_list = get_devices()
        print("deleting the flow entires ...............")
        for i in range (len(device_list)):
                flows_id = []
                url = base_url + "flows/" + device_list[i]
                handler = requests.get(url, auth=('onos','rocks'))
                flows_json = handler.json()
                for j in range (len(flows_json['flows'])):
                        if (flows_json['flows'][j]['appId'] == "org.onosproject.rest"):
                                flows_id.append(str(flows_json['flows'][j]['id']))
                for j in range (len(flows_id)):
                        url = base_url + "flows/" + device_list[i] + "/" + flows_id[j]
                        response = requests.delete(url, auth=('onos','rocks'))
                        print("flows is delete: " + device_list[i] + " " +flows_id[j])

#monitoring the shortest path connection
def continously_monitoring(path_list):
        while (1):
                for i in range (len(path_list)):
                        url = base_url + "devices/" + path_list[i][0] + "/ports"
                        handler = requests.get(url, auth=('onos','rocks'))
                        ports_json = handler.json()
                        for j in range (len(ports_json['ports'])):
                                if ports_json['ports'][j]['port'] == path_list[i][1]:
                                        if ports_json['ports'][j]['isEnabled'] == False :
                                                print("path is failed")
                                                return
        	time.sleep(3)


#generate the json for flow rule
def flow_rule_gen(s,port1,port2):
        data = json.loads(flow_json_example)
        data ['deviceId'] = s;
        data ['treatment']['instructions'][0]['port'] = port1
        data ['selector']['criteria'][0]['port'] = port2
        data_in_str = json.dumps(data)
        return data_in_str

if __name__ == '__main__':
	path = setup_flow(str(sys.argv[1]),str(sys.argv[2]))
	while(1):
		continously_monitoring(path)
		print("establishing new path..................")
		remove_all_flows()
		path = setup_flow(str(sys.argv[1]),str(sys.argv[2]))
