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

#get the url for networks
networks_url="$base_url:9696/v2.0/networks"
echo "networks url: $networks_url"

#get the url for subnets
subnets_url="$base_url:9696/v2.0/subnets"
echo "subnets url: $subnets_url"

#post Public network
PUBLIC_ID=$(curl -H "X-Auth-Token:$OS_TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{
    "network": {"name": "Public", "router:external": true}
}' \
-X POST "$networks_url" |\
python3 -c "import sys, json; print(json.load(sys.stdin)['network']['id'])") \
&& echo "POST Public network: $PUBLIC_ID"

#post Public subnet
PUBLIC_SUBNET_ID=$(curl -H "X-Auth-Token:$OS_TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{
    "subnet": {"name": "Public_subnet1",
"network_id": "'$PUBLIC_ID'",
"ip_version": 4,
"cidr": "172.24.4.0/24",
"gateway_ip": "172.24.4.1"
}
}' \
-X POST "$subnets_url" |\
python3 -c "import sys, json; print(json.load(sys.stdin)['subnet']['id'])") \
&& echo "POST Public subnet: $PUBLIC_SUBNET_ID"

#post BLUE network
BLUE_ID=$(curl -H "X-Auth-Token:$OS_TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{
    "network": {"name": "BLUE"}
}' \
-X POST "$networks_url" |\
python3 -c "import sys, json; print(json.load(sys.stdin)['network']['id'])") \
&& echo "POST BLUE network: $BLUE_ID"

#post BLUE subnet
BLUE_SUBNET_ID=$(curl -H "X-Auth-Token:$OS_TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{
    "subnet": {"name": "BLUE_subnet1",
"network_id": "'$BLUE_ID'",
"ip_version": 4,
"cidr": "10.0.0.0/24",
"gateway_ip": "10.0.0.1"
}
}' \
-X POST "$subnets_url" |\
python3 -c "import sys, json; print(json.load(sys.stdin)['subnet']['id'])") \
&& echo "POST BLUE subnet: $BLUE_SUBNET_ID"

#post RED network
RED_ID=$(curl -H "X-Auth-Token:$OS_TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{
    "network": {"name": "RED"}
}' \
-X POST "$networks_url" |\
python3 -c "import sys, json; print(json.load(sys.stdin)['network']['id'])") \
&& echo "POST RED  network: $RED_ID"

#post RED subnet
RED_SUBNET_ID=$(curl -H "X-Auth-Token:$OS_TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{
    "subnet": {"name": "RED_subnet1",
"network_id": "'$RED_ID'",
"ip_version": 4,
"cidr": "192.168.1.0/24",
"gateway_ip": "192.168.1.1"
}
}' \
-X POST "$subnets_url" |\
python3 -c "import sys, json; print(json.load(sys.stdin)['subnet']['id'])") \
&& echo "POST RED subnet: $RED_SUBNET_ID"

#get the url for routers
router_url="$base_url:9696/v2.0/routers"
echo "router url: $router_url"

ROUTER1_ID=$(curl -H "X-Auth-Token:$OS_TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{"router":{
"name": "router1",
"external_gateway_info":{"enable_snat":true,"network_id": "'$PUBLIC_ID'"}
}}' \
-X POST "$router_url" |\
python3 -c "import sys, json; print(json.load(sys.stdin)['router']['id'])") \
&& echo "POST router: $ROUTER1_ID"

#get the url for router1_add_interface
router1_add_interface_url="$router_url/$ROUTER1_ID/add_router_interface"
echo "router1 add interface url: $router1_add_interface_url"

#add router interface with BLUE network
curl -H "X-Auth-Token:$OS_TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{"subnet_id": "'$BLUE_SUBNET_ID'"}' \
-X PUT "$router1_add_interface_url"

#add router interface with RED network
curl -H "X-Auth-Token:$OS_TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{"subnet_id": "'$RED_SUBNET_ID'"}' \
-X PUT "$router1_add_interface_url"

#get image url
image_url="$base_url/image/v2/images"
echo "image url: $image_url"

#get server url
server_url="$base_url/compute/v2.1/servers"
echo "server url: $server_url"

#get the id of image cirros-0.3.5-x86_64-disk
export IMAGE_ID=$(curl -H "X-Auth-Token:$OS_TOKEN" "$image_url")
export IMAGE_ID=$(printf "import sys,os,json\ndata=json.loads(os.environ['IMAGE_ID'])\nfor x in data['images']:\n if x['name']=='cirros-0.3.5-x86_64-disk': print(x['id'])" | python)
echo "cirros-0.3.5-x86_64-disk image id: $IMAGE_ID"

#create instance
VM1_ID=$(curl -H "X-Auth-Token:$OS_TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{"server":{
"flavorRef": "42",
"name": "vm1",
"networks":[{"uuid": "'$PUBLIC_ID'"}],
"imageRef": "'$IMAGE_ID'"
}}' \
-X POST "$server_url" |\
python3 -c "import sys, json; print(json.load(sys.stdin)['server']['id'])") \
&& echo "vm1 id: $VM1_ID"

VM2_ID=$(curl -H "X-Auth-Token:$OS_TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{"server":{
"flavorRef": "42",
"name": "vm2",
"networks":[{"uuid": "'$BLUE_ID'"}],
"imageRef": "'$IMAGE_ID'"
}}' \
-X POST "$server_url" |\
python3 -c "import sys, json; print(json.load(sys.stdin)['server']['id'])") \
&& echo "vm1 id: $VM2_ID"

VM3_ID=$(curl -H "X-Auth-Token:$OS_TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{"server":{
"flavorRef": "42",
"name": "vm3",
"networks":[{"uuid": "'$RED_ID'"}],
"imageRef": "'$IMAGE_ID'"
}}' \
-X POST "$server_url" |\
python3 -c "import sys, json; print(json.load(sys.stdin)['server']['id'])") \
&& echo "vm1 id: $VM3_ID"


#get project url
project_url="$base_url/identity/v3/projects"
echo "project url: $project_url"

export PROJECT_ID=$(curl -H "X-Auth-Token:$OS_TOKEN" "$project_url")
export PROJECT_ID=$(printf "import sys,os,json\ndata=json.loads(os.environ['PROJECT_ID'])\nfor x in data['projects']:\n if x['name']=='admin': print(x['id'])" | python)

#get security group url
security_group_url="$base_url:9696/v2.0/security-groups"
echo "security group url: $security_group_url"

export SECURITY_GROUP_ID=$(curl -H "X-Auth-Token:$OS_TOKEN" "$security_group_url")
export SECURITY_GROUP_ID=$(printf "import sys,os,json\ndata=json.loads(os.environ['SECURITY_GROUP_ID'])\nfor x in data['security_groups']:\n if x['name']=='default' and x['project_id']=='$PROJECT_ID': print(x['id'])" | python)

#get security group rule url
security_group_rule_url="$base_url:9696/v2.0/security-group-rules"
echo "security group rule url: $security_group_rule_url"

#add icmp
curl -H "X-Auth-Token:$OS_TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{"security_group_rule":{"security_group_id": "'$SECURITY_GROUP_ID'",
"direction": "ingress",
"protocol": "icmp"
}}' \
-X POST "$security_group_rule_url"

curl -H "X-Auth-Token:$OS_TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{"security_group_rule":{"security_group_id": "'$SECURITY_GROUP_ID'",
"direction": "egress",
"protocol": "icmp"
}}' \
-X POST "$security_group_rule_url"
