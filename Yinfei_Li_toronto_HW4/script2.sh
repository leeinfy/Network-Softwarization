#!/bin/sh

#get the base url from script first argument
base_url="http://$1"
echo "base url: $base_url"

#get the url for getting token from openstack
token_url="$base_url/identity/v3/auth/tokens"
echo "token url: $token_url"

#Save a X-Subject-Token as env variable
resp=$(curl -i \
-H "Content-Type: application/json" \
-d '
{ "auth": {
"identity": {
"methods": ["password"],
"password": {
"user": {
"name": "admin",
"domain": { "id": "default" },
"password": "secret"
}
}
},
"scope": {
"project": {
"name": "admin",
"domain": { "id": "default" }
}
}
}
}' "$token_url" | grep X-Subject-Token | cut -d " " -f 2)
OS_TOKEN="$resp"
export OS_TOKEN=${OS_TOKEN//$'\015'}

#get project url
network_url="$base_url:9696/v2.0/networks"
echo "network url: $network_url"

export NETWORK=$(curl -H "X-Auth-Token:$OS_TOKEN" "$network_url")
export NETWORK=$(printf "import sys,os,json\ndata=json.loads(os.environ['NETWORK'])\nnetwork=[]\nfor x in data['networks']: network.append({'network_id':x['id'],'status':x['status']})\nprint(json.dumps(network))" | python)

#get project url
server_url="$base_url/compute/v2.1/servers/detail"
echo "network url: $server_url"

export INSTANCE=$(curl -H "X-Auth-Token:$OS_TOKEN" "$server_url")
export INSTANCE=$(printf "import sys,os,json\ndata=json.loads(os.environ['INSTANCE'])\ninstance=[]\nfor x in data['servers']: instance.append({'server_id':x['id'],'status':x['status']})\nprint(json.dumps(instance))" | python)

#get project url
port_url="$base_url:9696/v2.0/ports"
echo "port url: $port_url"

export ROUTER_INTERFACE=$(curl -H "X-Auth-Token:$OS_TOKEN" "$port_url")
export ROUTER_INTERFACE=$(printf "import sys,os,json\ndata=json.loads(os.environ['ROUTER_INTERFACE'])\nrouter_interface=[]\nfor x in data['ports']:\n if x['device_owner']=='network:router_interface': router_interface.append({'port_id':x['id'],'status':x['status']})\nprint(json.dumps(router_interface))" | python)

echo "{'status':{'networks':$NETWORK,'instances':$INSTANCE,'router_interface':$ROUTER_INTERFACE}}"


