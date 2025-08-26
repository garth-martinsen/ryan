# file: gui_client.py    purpose: liason between gui and adc_client thru db_server. runs in python3 env.
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

'''
class scheduler:
    def __init__(self):
        self.adc_client_ready = False
      
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
    return

def introduce_me():
    obj={"purpose" : '0',  "client_id" : "gui_client"}
    msg= json.dumps(obj)
    send(msg)

def send_ready():
    obj={"purpose" : '50', "client_id" : "gui_client"}
    msg= json.dumps(obj)
    send(msg)

    
def rqst_measure(chan):
    obj={"purpose" : '100', "chan": chan}
    msg= json.dumps(obj)
    send(msg)
    
def rqst_calibration(chan, vin):
    obj={"purpose" : '200', "chan": chan,"vin": vin}
    msg= json.dumps(obj)
    send(msg)

introduce_me()
send_ready()
rqst_measure(0)
rqst_calibration(1, 7.4)
 



#receive msg from server========blocking=============
amsg= client.recv(1012).decode(FORMAT)
if amsg:
    print(f"received msg:  {type(amsg)}  {amsg} ")
    msg=json.loads(amsg)
    purpose= msg['purpose']
    client_id = msg["client_id"]
    print(f"purpose: {purpose}  client_id: {client_id}")
#TODO: print out all msgs received from server