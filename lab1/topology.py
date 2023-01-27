from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def run():
	#create mininet object with limited CPU and shaped links
	net = Mininet(host = CPULimitedHost, link=TCLink)
	
	#create the network switches s1-s6
	s1,s2,s3,s4,s5,s6=[net.addSwitch(s) for s in 's1','s2','s3','s4','s5','s6']
	
	#create the network hosts h1-h3
	h1,h2,h3=[net.addHost(h,cpu=0.1) for h in 'h1','h2','h3']

	#add link between switch 10Mbps 5ms
	for (i,j) in [(s2,s1),(s2,s3),(s2,s5),(s2,s6)]:
		net.addLink(i,j,bw=10,delay='5ms')
	for (i,j) in [(s4,s1),(s4,s3),(s4,s5),(s4,s6)]:
		net.addLink(i,j,bw=10,delay='5ms')

	#add link between host and switch 5Mbps 10ms
	net.addLink(h1,s1,bw=5,delay='10ms')
	net.addLink(h2,s6,bw=5,delay='10ms')
	net.addLink(h3,s6,bw=5,delay='10ms')
	
	net.start()
	net.staticArp()
	CLI(net)

if __name__ == '__main__':
	setLogLevel( 'info' )
	run()
		
