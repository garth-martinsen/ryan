import socket
import json
from adc import ADC
from collections import OrderedDict
import time
from machine import RTC
#TODO: 8/11/25: Broken msg.purpose in adc_client.py. fix it.
adc = ADC()  #instantiate the adc. it will get cfg_ids and luts later from db_server requests.
rqsts_to_server=[]
rqsts_from_server =[]
respns_from_server=[]
respns_by_client=[]

purpose=' '
DISCONNECT_MESSAGE = '!DISCONNECT'
config_requests=[  '10', '20', '30', '40']
ranges_lut = {0: (30,46), 1: (60,91), 2: (90, 136)}  # used in step_calibrate
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
SERVER = '192.168.254.19'
stepdict=dict()
stepdict[0]= [3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5]
stepdict[1]=[6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8.0, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 9.0]
stepdict[2] =[9.0, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 11.0, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 12.0, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9, 13.0, 13.1, 13.2, 13.3, 13.4, 13.5]

# def calibrate(chan):
#     ''' This is a test method in adc_client to see if we can calibrate all vins in a channel'''
#     steps = stepdict[chan]
#     for vin in steps:
#         obj = adc.calibrate(chan, 'calibrate', vin) 
#         #obj= {"purpose":'200', "chan" : chan, "vin": vin}
#         payload= json.dumps(obj)
#         time.sleep(1)
#         input(f" Press return to send msg to server for chan: {chan}, vin: {vin}")
#         print( "sending to server: ", payload)
#         send(payload)
#     print(f'Done calibrating channel: {chan}')

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

#receive msg from server========blocking=============
    msg= client.recv(1012)
    print("received msg: ", msg)
    jsonx= json.loads(msg.decode(FORMAT))
    purpose = jsonx["purpose"]
    if purpose == "1":
        configure()    
    if purpose == '11':
        adc.cfg_ids = tuple(jsonx["cfg_ids"])
        respns_from_server.append(f"{purpose}")
    elif purpose in ['21','31','41'] :
        channel = jsonx['chan']
        adc.luts[channel]= convert_to_dict(jsonx['lut'])
    elif purpose == '100' : #measure
        #TODO: Done: Implement  response(101) to svr request to call adc.measure(channel) and return report to svr.
        chan = jsonx['chan']
        print(f"Server CMD: purpose: {purpose} channel: {chan}  is requested by server...")
        time.sleep(2)
        results = adc.measure(chan, 'measure')
        respns_by_client.append(f"Sent Client response(101) to Server rqst({purpose}: {chan})")
        rqsts_from_server.append(f"100 purpose: {purpose}")
        # 101 means report from client for a server 100 msg.
        payload=json.dumps(results)
        send(payload)
    elif purpose == '200':  # calibrate
       chan = jsonx['chan']
       vin = jsonx['vin']
       print(f"Server CMD:  purpose: {purpose} channel: {chan} vin: {vin} is requested by server...")
       results = adc.calibrate(chan,'calibrate',vin)
       #TODO: Find out why adc.calibrate returns results=null in adc_client(line 87)  client.recv(1012) (blocking )
       print("line 88 client.recv() results: ", results)
       rqsts_from_server.append(f"calibrate {chan} for {vin} ")
       respns_by_client.append("Sent Client response(201) to Server chan:{chan}. vin: {vin}")
       payload = json.dumps(results)
       print(f"payload for : {purpose}  {payload}")
       send(payload)

def convert_to_dict(lut):
    # print("converting lut: ")
    #create dict to return for assignment to adc. works for all channels
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
    print("respns_from_Client: ", respns_by_client)
#     if isconfigured():
#         print("adc client is totally configured and ready to respond to server cmds.")

def isconfigured():
    cfgOK= adc.cfg_ids != 0
    lut0OK = len(adc.luts[0]) > 14  #should be 15
    lut1OK = len(adc.luts[1]) > 30  #should be 31
    lut2OK = len(adc.luts[2]) > 43  #should be 44
    return cfgOK and lut0OK and lut1OK and lut2OK
           
def configure():
    for num in config_requests:
        obj={"purpose": str(num)}
        msg = json.dumps(obj)
        send(msg)
        rqsts_to_server.append(msg)
    if isconfigured():
        obj={"purpose": '50'}
        msg=json.dumps(obj)
        send(msg)
        rqsts_to_server.append(msg)      
        print("The adc client is totally configured and ready to respond to server cmds.")
        print("========Server CMDS=========")
        
# temp method. Delete when scheduler is working.        
# def do_something():
#     #send calibrate msg to server
#     if isconfigured():
#         chan=0
#         send(json.dumps(adc.calibrate(chan, 'calibrate', 3.0)))
#         
    #send(DISCONNECT_MESSAGE)
obj={"purpose": '0', "greet": "Hello, I am adc_client", "client_id": "adc_client"}
msg= json.dumps(obj)
send(msg)
 
configure()

log()



# def calibrate_chan(chan,vin):
#     '''Utility ... Called from step_calibrate,which changes vin
#      will send to server with send(payload)'''
#     purpose="calibrate"
#     payload = adc.calibrate(chan, purpose, vin)
#     print("payload: ", payload)
#     send(payload)
#     
# def step_calibrate(chan):
#     '''This method allows user to build the LUT for  chan x
#      Hitting return key calls next vin'''
#     (start, stop)  = ranges_lut[chan]
#     for i in range(start,stop):
#        input(f"Press Enter when power supply is set to {i/10}.")  
#        calibrate_chan(chan, i/10)
# when server sends:  {"purpose": "measure", "channel": 0}
# def measure_chan(chan):
#     if len(cmds) and cmds.pop():
#         send(adc.measure(chan, purpose))
#  
 