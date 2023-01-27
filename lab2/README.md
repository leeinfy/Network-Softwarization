Run `/opt/onos/bin/onos-service` to enable ONOS serivce <br>
Use `sudo python topo.py` to setup mininet <br>
Make sure the topo graph is same as figure, 3 devices, 2 hosts, 6 link<br>
![topology gui](topo.png "topology gui")
Mininet command `h1 ping h2` or `h2 ping h1` do not work<br>
Then Run command `python flows.py` in a new terminal<br> 
Mininet command `h1 ping h2` or `h2 ping h1` would work<br>
Then run command `link s1 s2 down` in mininet<br>
In `flows.py` terminal will indicate the path is fail and then replace with a new flow entries
![terminal result](output.png "terminal result")
<br>
<br>
Any json error is caused by ONOS fail to find all the links, hosts, or devices <br>
Use `links`, `devices`, `hosts` to varify your mininet topology is ONOS<br>
The path setup is base on REST api of ONOS, if there is not result using `paths` command, the `flows.py` will fail

