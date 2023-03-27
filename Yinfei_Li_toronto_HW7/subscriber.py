"""
Created: Mar, 2023
@author: Morteza Moghaddassian
@Project: NetSoft Technology Course
"""
# paho is a client library to communicate with Mosquitto broker that implements MQTT V3.1.1
import paho.mqtt.client as paho
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv
import pandas as pd
import time as clock
import threading

def countdown():
    global my_timer

    my_timer = 7200

    for x in range(7200):
        my_timer = my_timer-1
        clock.sleep(1)

countdown_thread = threading.Thread(target = countdown)
countdown_thread.start()

#create an empty csv file or clear the previous file
file=open('output.csv', 'w')
fieldnames = ["Time", "CPU", "Total_Memory", "Free_Memory", "Used_Memory", "Percentage_Utilization", "Bytes_Sent", "Bytes_Receive"]
thewriter = csv.DictWriter(file,fieldnames=fieldnames)
thewriter.writeheader()
file.close()
  
'''
    @class_name: Subscriber
    @role: Subscribing for contents and keeping them in memory.
    @number of methods: 4
    @access modifier: public    
'''
class Subscriber:
    # The topic that the subscriber needs to use for receiving the content from the message broker.
    subscriber_topic = None
    # Broker IP address.
    broker_address = None
    # The port that the broker is listening on for incoming connections. The default is 1883 for Mosquitto broker.
    broker_port = None    
    # Is used to save the message received from the broker.
    message_received = ''    

    '''
        @input: address, port, topic
        @role: Constructor method
    '''
    def __init__(self, address, port, topic):
        # The broker IP address (142.1.174.167)
        self.broker_address = str(address)
        # The broker port number (1883)
        self.broker_port = int(port)
        # Subscription Topic
        self.subscriber_topic = str(topic)        
       

    '''
        @input: client, userdate, flags, rc
        @role: Is being used to pair with the on_connect method on the broker to exchange the subscription topic.
    '''
    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.subscriber_topic)

    '''
        @input: client, userdata, message
        @role: Is being used to pair with the on_message method on the broker to exchange the message with the topic of interest.
    '''
    #callback function with subscribed topic
    def on_message(self, client, userdata, message):
        pass

    #callback function of each sub topic 
    def on_message_Time(self, client, userdata, message):
        global time
        time = str(message.payload,encoding='utf-8')

    def on_message_CPU(self, client, userdata, message):
        global cpu
        cpu = str(message.payload,encoding='utf-8')

    def on_message_Total_Memory(self, client, userdata, message):
        global total_memory
        total_memory = str(message.payload,encoding='utf-8')

    def on_message_Free_Memory(self, client, userdata, message):
        global free_memory
        free_memory = str(message.payload,encoding='utf-8')

    def on_message_Used_Memory(self, client, userdata, message):
        global used_memory
        used_memory = str(message.payload,encoding='utf-8')

    def on_message_Percentage_Utilization(self, client, userdata, message):
        global percentage_utilization
        percentage_utilization = str(message.payload,encoding='utf-8')


    def on_message_Bytes_Sent(self, client, userdata, message):
        global byte_sent
        byte_sent = str(message.payload,encoding='utf-8')

    def on_message_Bytes_Receive(self, client, userdata, message):
        global byte_receive
        byte_receive = str(message.payload,encoding='utf-8')
        #save the topic is come in sequence, save the result in csv file
        df=pd.DataFrame({'Time': time, 
                         'CPU':cpu, 
                         'Total_Memory':total_memory, 
                         'Free_Memory':free_memory, 
                         'Used_Memory':used_memory, 
                         'Percentage_Utilization':percentage_utilization, 
                         'Bytes_Sent':byte_sent, 
                         'Bytes_Receive':byte_receive}, index=[0])
        df.to_csv("output.csv", mode='a', index=False,header=False)
        #only disconnect with the last sequence of send, this would not cause a data lose
        client.disconnect()

    '''
        @role: Subscribing to the broker and enabling the retrieval of the contents specified by the topics of interest.
    '''
    def subscribe(self):
        # Creating an MQTT client object.
        sub = paho.Client()
        # An infinite loop to keep the subscriber alive.
        while True:
            # Connecting to the broker.
            sub.connect(self.broker_address, self.broker_port)
            #add the sub topic callback function
            sub.message_callback_add("lab7/netsoft10/Time", self.on_message_Time)
            sub.message_callback_add("lab7/netsoft10/CPU", self.on_message_CPU)
            sub.message_callback_add("lab7/netsoft10/Total_Memory", self.on_message_Total_Memory)
            sub.message_callback_add("lab7/netsoft10/Free_Memory", self.on_message_Free_Memory)
            sub.message_callback_add("lab7/netsoft10/Used_Memory", self.on_message_Used_Memory)
            sub.message_callback_add("lab7/netsoft10/Percentage_Utilization", self.on_message_Percentage_Utilization)
            sub.message_callback_add("lab7/netsoft10/Bytes_Sent", self.on_message_Bytes_Sent)
            sub.message_callback_add("lab7/netsoft10/Bytes_Receive", self.on_message_Bytes_Receive)
            sub.on_message = self.on_message
            # Providing the topic of interest.
            sub.on_connect = self.on_connect
            # Keep the subscriber running until the whole message is received.
            sub.loop_forever()
            if my_timer == 0:
                break

if __name__ == "__main__":       
    broker_address = "142.1.174.167"
    broker_port = 1883        
    # Topics that are used to subscribe for the data.
    subscriber_topic = "lab7/netsoft10/#"
    # Instantiate an object of type Subscriber
    subscriber = Subscriber(broker_address,broker_port, subscriber_topic)
    subscriber.subscribe()

    #Plot the data from csv file
    df = pd.read_csv('output.csv')
    xdata = df['Time']
    ydata1 = df['CPU']
    ydata2 = df['Total_Memory']
    ydata3 = df['Free_Memory']
    ydata4 = df['Used_Memory']
    ydata5 = df['Percentage_Utilization']
    ydata6 = df['Bytes_Sent']
    ydata7 = df['Bytes_Receive']

    fig, ax = plt.subplots(4,2)
    fig.tight_layout()
    ax[0][0].set_title('CPU')
    ax[0][0].plot(xdata, ydata1)
    ax[0][1].set_title('Total_Memory')
    ax[0][1].plot(xdata, ydata2)
    ax[1][0].set_title('Free_Memory')
    ax[1][0].plot(xdata, ydata3)
    ax[1][1].set_title('Used_Memory')
    ax[1][1].plot(xdata, ydata4)
    ax[2][0].set_title('Percentage_Utilization')
    ax[2][0].plot(xdata, ydata5)
    ax[2][1].set_title('Bytes_Sent')
    ax[2][1].plot(xdata, ydata6)
    ax[3][0].set_title('Bytes_Receive')
    ax[3][0].plot(xdata, ydata7)
    plt.show()

   
