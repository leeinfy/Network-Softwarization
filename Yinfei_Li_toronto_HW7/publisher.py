"""
Created: Mar, 2023
@author: Morteza Moghaddassian
@Project: NetSoft Technology Course
"""
# Python Installation: pip3 install paho-mqtt (V3.1)
# paho is a client library to communicate with Mosquitto broker that implements MQTT V3.1.1 (MMG)
import paho.mqtt.client as paho
import time as clock
import psutil
from itertools import count

index = count()

'''
    @class_name: Publisher
    @role: Publishing contents to the message broker.
    @number of methods: 3
    @access modifier: public    
'''
class Publisher:
    # The broker address.
    broker_address = None
    # The port that the broker is listening on for incoming connections. The default is 1883 for Mosquitto broker.
    broker_port = None

    '''
        @input: address, port
        @role: Constructor method
    '''
    def __init__(self, address, port):
        # The broker IP address (142.1.174.167)
        self.broker_address = address
        # The broker port number (1883)
        self.broker_port = int(port)

    def on_publish(self,client,userdata,result):
        pass

    '''
        @input: topic, message (The content that has to be published).
        @role: Publishing the message to the broker.
        @info: This method maintains a request-respond model with the caller.
    '''
    def publish(self, topic, message):
        # Creating a paho (MQTT) client object.
        pub = paho.Client()
        pub.on_publish = self.on_publish
        # Connecting the "pub" object to the message broker.
        pub.connect(self.broker_address,self.broker_port)
        # Publishing the data.

        answer = pub.publish(topic, message)
        print("Published "+topic+" number "+message)
        # Disconnecting the client paho (MQTT) objecct.
        pub.disconnect()


if __name__ == "__main__":       
    broker_address = "142.1.174.167"
    broker_port = 1883        
    # Instantiate an object of type Publisher
    publisher = Publisher(broker_address, broker_port)
    #the time interval is 2, so to continously monitor 2 hours need 3600 iteration
    #imer_start = clock.time()
    while True:
        #publish timer index
        publisher.publish("lab7/netsoft10/Time",str(next(index)))
        #timer_now = clock.time()
        #publisher.publish("lab7/netsoft10/Time",str(timer_now-timer_start))
    	#get cpu percent and publish to MQTT broker
        string = str(psutil.cpu_percent())
        publisher.publish("lab7/netsoft10/CPU",string)
        #get memory and publish to MQTT broker
        memory = psutil.virtual_memory()           
        publisher.publish("lab7/netsoft10/Total_Memory",str(memory.total))
        publisher.publish("lab7/netsoft10/Free_Memory",str(memory.free))
        publisher.publish("lab7/netsoft10/Used_Memory",str(memory.used))
        publisher.publish("lab7/netsoft10/Percentage_Utilization",str(memory.percent))
        #get network io and publish to MQTT broker
        network = psutil.net_io_counters()
        publisher.publish("lab7/netsoft10/Bytes_Sent",str(network.bytes_sent))
        publisher.publish("lab7/netsoft10/Bytes_Receive",str(network.bytes_recv))
        # Adds delay
        clock.sleep(1)
