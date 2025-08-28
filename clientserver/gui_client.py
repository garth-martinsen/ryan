# file: gui_client.py    purpose: liason between gui and adc_client thru db_server. runs in python3 env.
# ref: https://github.com/juliogema/python-basic-socket/blob/main/client.py

import socket
import json
from collections import OrderedDict
import time
# import asyncio

class gui_data:
    def __init__(self):
        self.client_name=''
        self.cfg_ids=()
        self.luts = [{},{},{}]
        self.configs = []               # all fields in CONFIG table (except luts)
        self.measurements=[]    # all records from BMS table where type='m'
        self.calibrations=[]          # all records from BMS table where type='c'
        
    def __str__(self):
       return f" {self.client_name}  cfg_ids: {self.cfg_ids}  configurations: {self.configs}  luts: {self.luts}  measurements: {self.measurements}  calibrations: {self.calibrations}"
        
gui_data = gui_data()
svr_msgs_cnt=0        

'''ADC  Configure includes [10,20,30,40,50]  50 tells server that adc_client is READY
... Following wait for 50 (READY MSG)
100: measure(chan)
200: calibrate(chan, vin)
300: repeating measurement sequence includes [3 measure(chan), 1 wait]
400: repeating calibration sequence includes 3 sets of stepping vins with
delay to set Power supply. '''
 
#=======client code=========    
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
SERVER = '192.168.254.19'
ADDR = (SERVER, PORT)
resps_from_svr = []
rqsts_to_svr = []

def convert_to_dict(lut):
    # print("converting lut: ")
    #create dict to return for assignment to adc. works for all channels
    lutx={}
    for k,v in lut.items():
        lutx[float(k)]=v
    return OrderedDict(sorted(lutx.items()))

def introduce_me():
    obj={"purpose" : '0',  "client_id" : "gui_client"}
    rqsts_to_svr.append(0)
    msg= json.dumps(obj)
    send(msg)

def send_ready():
    obj={"purpose" : '50', "client_id" : "gui_client"}
    rqsts_to_svr.append(50)
    msg= json.dumps(obj)
    send(msg)

    
def rqst_measure(chan):
    rqsts_to_svr.append(100)
    obj={"purpose" : '100', "chan": chan}
    msg= json.dumps(obj)
    send(msg)
    
def rqst_calibration(chan, vin):
    rqsts_to_svr.append(200)
    obj={"purpose" : '200', "chan": chan,"vin": vin}
    msg= json.dumps(obj)
    send(msg)

def configure_gui_client():
    global msg, conn, addr 
    rqsts = [10,20,30,40]
    for num in rqsts:
        rqsts_to_svr.append(num)
        obj = {"purpose": num}
        msg = json.dumps(obj)
        send(msg)

def actions():
    introduce_me()
    configure_gui_client()
    send_ready()
    rqst_measure(0)
    rqst_calibration(1, 7.4)

def log():
    print("gui_data: ",  gui_data.__str__())
    print(f"rqsts_to_server: {rqsts_to_svr} ")
    print(f"resps_from_server: {resps_from_svr} ")
    print(f"server msgs_count: {svr_msgs_cnt}")
 

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    global svr_msgs_cnt
    message = msg.encode(FORMAT)
    if message:
        msg_len = len(message)
        send_length = str(msg_len).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)
    #receive msg from server========blocking method =============
        amsg= client.recv(1012).decode(FORMAT)
        svr_msgs_cnt +=1
        if amsg:
            msg=json.loads(amsg)
            print(f" type: {type(msg)} msg: {msg} ")
            purpose= msg['purpose']
            resps_from_svr.append(purpose)
            #TODO: Decide if every msg should have client_id field. Causing error here.
            # client_id = msg["client_id"]
            print(f"purpose: {purpose}  msg: { msg }")
        #TODO: print out all msgs received from server
            if purpose == 1:
                client_id = msg["client_id"]
                gui_data.client_name = client_id
            elif purpose == 11:      
                gui_data.cfg_ids = tuple(msg["cfg_ids"])
            elif purpose in [21, 31, 41] :
                chan = msg["chan"]
                lut= msg["lut"]
                gui_data.luts[chan] = convert_to_dict(lut)
            elif purpose == 51:
                print("Gui_client is ready to send and receive msgs from adc_client.")
                
actions()
log()       
