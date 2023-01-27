from mininet.net import Mininet
from mininet.node import Node, RemoteController
from mininet.cli import CLI
from mininet.node import CPULimitedHost
from mininet.log import setLogLevel, info


def run():
	net = Mininet(host=CPULimitedHost,autoSetMacs=True, cleanup=True)
	s1,s2,s3 = [net.addSwitch(s) for s in  's1','s2','s3']
	h1,h2= [net.addHost(h,cpu=0.1) for h in 'h1','h2']

	net.addLink(s1, s2)
 	net.addLink(s2, s3)
  	net.addLink(s3, s1)
    	net.addLink(h1, s1)
	net.addLink(h2, s2)
	
	c1 = RemoteController('c1', ip='127.0.0.1', port=6653)
  	net.addController(c1)

	net.start()
	net.staticArp()
	CLI(net)
	
if __name__ == '__main__':
	setLogLevel('info')
	run()