# file: adc_client.py
# ref: https://github.com/juliogema/python-basic-socket/blob/main/client.py
# ref: https://duckduckgo.com/?q=tech+with+tim+socket+programming&atb=v314-1&ia=videos&iax=videos&iai=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QiPPX-KeSc
import socket
import json
from adc import ADC
from collections import OrderedDict
import time

#TODO: Have to Control-C and issue calls : hi(), config(10), config(20), config(30), config(40). They work to configure adc but clumsy.
adc = ADC()  #instantiate the adc. it will get cfg_ids and luts later from db_server requests.
rqsts_to_server=[]
rqsts_from_server =[]
respns_from_server=[]
respns_by_client=[]

purpose=' '
DISCONNECT_MESSAGE = '!DISCONNECT'
config_requests=[10, 20, 30, 40]
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
SERVER = '192.168.254.19'
ADDR = (SERVER, PORT)

# greet and register with server
def hi():
    obj={"purpose": 0, "client_id": "adc_client"}
    msg= json.dumps(obj)
    rqsts_to_server.append(0)
    send(msg)
    return

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
    time.sleep(1)
    rqsts_to_server.append(msg["purpose"])
 
    #send(DISCONNECT_MESSAGE)
def send_ready(num):
    obj={"purpose": num}
    msg=json.dumps(obj)
    send(msg)
    rqsts_to_server.append(msg["purpose"])
    conn.send(msg)
    print("The adc client is totally configured and ready to respond to server cmds.")
    
def log():
    print()
    print("Log of client-server traffic since client startup:")
    print("rqsts_to_server: ", rqsts_to_server)
    print("respns_from_server: ", respns_from_server)
    print("rqsts_from_server: ", rqsts_from_server)
    print("respns_from_Client: ", respns_by_client)

def isconfigured():
    cfgOK= adc.cfg_ids != 0
    lut0OK = len(adc.luts[0]) > 14  #should be 15
    lut1OK = len(adc.luts[1]) > 30  #should be 31
    lut2OK = len(adc.luts[2]) > 43  #should be 44
    return cfgOK and lut0OK and lut1OK and lut2OK

def config_all():
    for num in config_requests:
        config(num)
        
def config(num):
        obj={"purpose": num}
        msg = json.dumps(obj)
        send(msg)
        rqsts_to_server.append(msg["purpose"])
        return

        print("========Server CMDS=========")

#print('sending to db_server at ADDR: ', ADDR)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    '''Receives a string, encodes into bytes, sends len and message'''
    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_length = str(msg_len).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    #receive msg from server========blocking=============
    while True:
        amsg = client.recv(2048).decode(FORMAT)
        #TODO 3: Leading text in received msg breaks json.loads(). Need first char to be '{ and last char to be }'
        # Finish the following and test it thoroughly.
        #print(f"amsg received from svr : { type(amsg)}  {amsg}")
        if not amsg:
            continue
        rmsg = json.loads(amsg)
       
        print(f" rmsg: {type(rmsg)} {rmsg}") # rmsg is hopefuly a dict 
        purpose = rmsg["purpose"]
        if purpose == 1:
            respns_from_server.append(f"{purpose}")
            config(10)    #rqst cfg_ids
        elif purpose == 11:
            respns_from_server.append(f"{purpose}")
            adc.cfg_ids = tuple(rmsg["cfg_ids"])
            config(20)    #rqst lut[0]
        elif purpose == 21 :
            print(f" ******Handling purpose: {purpose}*****")
            respns_from_server.append(f"{purpose}")
            '''channel and lut '''
            chan = rmsg["chan"]
            lut= rmsg["lut"]
            adc.luts[chan]= convert_to_dict(lut)
            config(30)    #rqst lut[1]
        elif purpose == 31 :
            print(f" ******Handling purpose: {purpose}*****")
            respns_from_server.append(f"{purpose}")
            '''Channel and lut '''
            chan = rmsg["chan"]
            lut= rmsg["lut"]
            adc.luts[chan]= convert_to_dict(lut)
            config(40)    #rqst lut[2]
        elif purpose == 41 :
            print(f" ******Handling purpose: {purpose}*****")
            respns_from_server.append(f"{purpose}")
            '''channel and lut '''
            chan = rmsg["chan"]
            lut = rmsg["lut"]
            adc.luts[chan] = convert_to_dict(lut)
            if isconfigured():
                send_ready(50)      #notify svr that adc_client is ready
        elif purpose == 51:
            print("server knows that adc_client is ready for requests.")
        elif purpose == 100 : #measure
            rqsts_from_server.append(f"100 purpose: {purpose}")
            chan = rmsg['chan']
            print(f"Server CMD: purpose: {purpose} channel: {chan}  is requested by server...")
            time.sleep(1)
            results = adc.measure(chan, 'measure')
            respns_by_client.append(f"Sent Client response(101) to Server rqst({purpose}: {chan})")
            # 101 means report from client for a server 100 msg.
            payload=json.dumps(results)
            send(payload)
        elif purpose == 200:  # calibrate
           chan = rmsg['chan']
           vin = rmsg['vin']
           print(f"Server CMD:  purpose: {purpose} channel: {chan} vin: {vin} is requested by server...")
           results = adc.calibrate(chan,'calibrate',vin)
           print("line 88 client.recv() results: ", results)
           rqsts_from_server.append(f"{purpose} {chan} for {vin} ")
           respns_by_client.append("Sent Client response(201) to Server chan:{chan}. vin: {vin}")
           payload = json.dumps(results)
           print(f"payload for : {purpose}  {payload}")
           send(payload)

hi()
config(10)
config(20)
config(30)
config(40)        


log()

