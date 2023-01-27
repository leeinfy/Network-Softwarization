#!/bin/bash

#h1->h2
ovs-ofctl add-flow s1 in_port=3,dl_type=0x0800,nw_src=10.0.0.1,nw_dst=10.0.0.2,action:output=1
ovs-ofctl add-flow s2 in_port=1,dl_type=0x0800,nw_src=10.0.0.1,nw_dst=10.0.0.2,action:output=4
ovs-ofctl add-flow s6 in_port=1,dl_type=0x0800,nw_src=10.0.0.1,nw_dst=10.0.0.2,action:output=3

#h2->h1
ovs-ofctl add-flow s6 in_port=3,dl_type=0x0800,nw_src=10.0.0.2,nw_dst=10.0.0.1,action:output=1
ovs-ofctl add-flow s2 in_port=4,dl_type=0x0800,nw_src=10.0.0.2,nw_dst=10.0.0.1,action:output=1
ovs-ofctl add-flow s1 in_port=1,dl_type=0x0800,nw_src=10.0.0.2,nw_dst=10.0.0.1,action:output=3


#h1->h3
ovs-ofctl add-flow s1 in_port=3,dl_type=0x0800,nw_src=10.0.0.1,nw_dst=10.0.0.3,action:output=2
ovs-ofctl add-flow s4 in_port=1,dl_type=0x0800,nw_src=10.0.0.1,nw_dst=10.0.0.3,action:output=4
ovs-ofctl add-flow s6 in_port=2,dl_type=0x0800,nw_src=10.0.0.1,nw_dst=10.0.0.3,action:output=4

#h3->h1
ovs-ofctl add-flow s6 in_port=4,dl_type=0x0800,nw_src=10.0.0.3,nw_dst=10.0.0.1,action:output=2
ovs-ofctl add-flow s4 in_port=4,dl_type=0x0800,nw_src=10.0.0.3,nw_dst=10.0.0.1,action:output=1
ovs-ofctl add-flow s1 in_port=2,dl_type=0x0800,nw_src=10.0.0.3,nw_dst=10.0.0.1,action:output=3