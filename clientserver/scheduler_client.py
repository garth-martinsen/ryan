# file: scheduler_client.py    purpose: liason between gui and adc_client thru db_server. runs in python3 env.
# ref: https://github.com/juliogema/python-basic-socket/blob/main/client.py

import socket
import json
from collections import OrderedDict
import time
import asyncio

'''ADC  Configure includes [10,20,30,40,50]  50 tells server that adc_client is READY
... Following wait for 50 (READY MSG)
100: measure(chan)
200: calibrate(chan, vin)
300: repeating measurement sequence includes [3 measure(chan), 1 wait]
400: repeating calibration sequence includes 3 sets of stepping vins with
delay to set Power supply. '''

stepdict=dict()
stepdict[0]= [3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5]
stepdict[1]=[6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8.0, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 9.0]
stepdict[2] =[9.0, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 11.0, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 12.0, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9, 13.0, 13.1, 13.2, 13.3, 13.4, 13.5]

'''
class scheduler:
    def __init__(self):
        self.adc_client_ready = False
        self.step_dict = stepdict
        self.socket = client

    def on_demand_measure(self, chan):
        pass
 
    def on_demand_calibrate(self, chan):
        pass
    
    def schedule(self):
        pass
    
    def fetch_history(self):
        pass
    
    def fetch_samples(self, chan):
        pass
    
    def fetch_lut(self, chan):
        pass
'''    
#=======client code=========    
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
SERVER = '192.168.254.19'
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_length = str(msg_len).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))

    client.send(send_length)
    client.send(message)

obj={"purpose" : '0', "greet": "Hello, I am the Scheduler", "client_id" : "scheduler_client"}
msg= json.dumps(obj)
send(msg)

    
#receive msg from server========blocking=============
msg= client.recv(1012)
print("received msg: ", msg)
'''
jsonx= json.loads(msg.decode(FORMAT))
purpose = jsonx["purpose"]
chan = jsonx['chan']

if purpose == '50':
    print("scheduler.adc_client_ready=True")


elif purpose == '100'
    msg={"purpose": '100', "chan":  chan}
    send(str(msg))
elif purpose == '200'
    msg={"purpose": '100', "chan":  chan}
    send(str(msg))
'''    

    
