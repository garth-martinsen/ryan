import socket
import json
from adc import adc
from collections import OrderedDict
import time

adc = adc()  #instantiate the adc. it will get cfg_ids and luts later from db_server requests.

rqsts_to_server =[]
rqsts_from_server =[]
respns_from_server=[]
actions_by_client=[]
purpose=' '
DISCONNECT_MESSAGE = '!DISCONNECT'
server_requests=['10', '20', '30', '40']
ranges_lut = {0: (30,46), 1: (60,91), 2: (90, 136)}  # used in step_calibrate

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
SERVER = '192.168.254.19'

# when server sends:  {"purpose": "measure", "channel": 0}
def measure_chan(chan):
    if len(cmds) and cmds.pop():
        send(adc.measure(chan, purpose))
        
#when server sends:  {"purpose": "calibrate", "channel": 0, "Vin": 3.2}           
def calibrate_chan(chan,vin):
    '''Called from step_calibrate, or from server request.
     if from server, send(payload)'''
    purpose="calibrate"
    payload = adc.calibrate(chan, purpose, vin)
    print("payload: ", payload)
    # send(payload)
    
def step_calibrate(chan):
    '''This method allows user to build the LUT for  chan x
     without server involvement.
     Hitting return key calls next vin'''
    (start, stop)  = ranges_lut[chan]
    for i in range(start,stop):
       input()  # allows user to control when it fires: upon return key
       calibrate_chan(chan, i/10)


ADDR = (SERVER, PORT)
print('sending to db_server at ADDR: ', ADDR)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_length = str(msg_len).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

#receive msg from server
    msg= client.recv(1012)
    jsonx= json.loads(msg.decode(FORMAT))
    purpose = jsonx["purpose"]
    if purpose == '10':
        adc.cfg_ids = tuple(jsonx["cfg_ids"])
        respns_from_server.append(f"{purpose}")
    elif purpose in ['20','30','40'] :
        channel = jsonx['chan']
        adc.luts[channel]=convert_to_dict(jsonx['lut'])
        respns_from_server.append(f"{purpose} {channel}")
    elif purpose == '100' :
        #TODO: Done: Implement  response to svr request to call adc.measure(channel) and return report to svr.
        chan = jsonx['chan']
        print(f" purpose: {purpose} channel: {chan}  is requested by server...")
        time.sleep(2)
        results = adc.measure(chan, 'measure')
        actions_by_client.append("Ready to send the Client response the Server for to 100: 0")
        rqsts_from_server.append(f"{purpose}: {purpose}")
        # 101 means report from client for a server 100 msg.
        payload=json.dumps(results)
        send(payload)
    elif purpose == '200':
       chan = jsonx['chan']
       vin = jsonx['vin']
       print(f" purpose: {purpose} channel: {chan}  is requested by server...")
       adc.calibrate(chan,'calibrate',vin)
       rqsts_from_server.append(f"calibrate {chan} for {vin} ")
       
def convert_to_dict(lut):
    # print("converting lut: ")
    #create dict to return
    lutx={}
    for k,v in lut.items():
        lutx[float(k)]=v
    return OrderedDict(sorted(lutx.items()))

# requests to the server to download luts and cfg_ids
def server_request(msg):
    send(msg)
    time.sleep(2)
    rqsts_to_server.append(msg)
 
    #send(DISCONNECT_MESSAGE)

def log():
    print()
    print("Log of client-server traffic since client startup:")
    print("rqsts_to_server: ", rqsts_to_server)
    print("respns_from_server: ", respns_from_server)
    print("rqsts_from_server: ", rqsts_from_server)
    print("Actions by Client: ", actions_by_client)
    if isconfigured():
        print("adc client is totally configured and ready to respond to server cmds.")

def isconfigured():
    cfgOK= adc.cfg_ids != 0
    lut0OK = len(adc.luts[0]) > 14  #should be 15
    lut1OK = len(adc.luts[1]) > 30  #should be 31
    lut2OK = len(adc.luts[2]) > 43  #should be 44
    return cfgOK and lut0OK and lut1OK and lut2OK
           
def configure():
    for msg in server_requests:
        send(msg)
        rqsts_to_server.append(msg)
    if isconfigured():
        print("The adc client is totally configured and ready to respond to server cmds.")
        send('50')
        rqsts_to_server.append('50')
    #send(DISCONNECT_MESSAGE)
configure()   
log()


