import socket
import threading
from data_controller import DataController
import json
from collections import namedtuple
from database_interface import BMS, CALIBRATE
import time

''' This server is implemented in python3. It can receive requests from clients running in either
python3 or micropython. It is multi-threaded and can handle many clients.
In messages to/from clients, the payload will be in json. The first json field
will be "purpose" so that the server/client can branch to perform processing
to handle the msg.'''

HEADER = 64  # bit
PORT = 5050
SERVER = '192.168.254.19'   #the host computer running in python3
# SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECTED"
#client requests/notification to server...
CFG_IDS                = '10'
LUT0                       = '20'
LUT1                       = '30'
LUT2                       = '40'
CLIENT_READY    = '50'  #sent when totally configured...
# server_msgs or commands...
MEASURE                    = '100'
CONFIGURE                = '200'
# client responses to server commands...
MEASURE_RSPNS     = '101'
CALIBRATE_RSPNS   = '201'

#load configuration from db . You need to furnish your ids in the place of (1,2,3) .
dc=DataController((1,2,3))  #put your ids tuple here.

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

client_initiated_msgs=[]
server_initiated_msgs=[]

# remove actions dict if not useful to user...
actions= dict()

def load_actions_for_msgs():
      actions[ CFG_IDS ] = self.dc.cfg_ids
      actions[LUT0] = self.dc.luts[0]
      actions[LUT1] = self.dc.luts[1]
      actions[LUT2] = self.dc.luts[2]
      actions[CLIENT_READY] = 'Ready to send cmds to client to Measure or Configure .'

# remove this if it is not useful to the user...
meanings=dict()

def load_meanings():
        meanings[10]=" client requests cfg_ids "
        meanings[20]= " client requests lookup table for channel 0"
        meanings[30]= " client requests lookup table for channel 1"
        meanings[40]= " client requests lookup table for channel 2"
        meanings[50]= " client reports that it is ready for server cmds"
        meanings[100]= " Server cmds client to measure  a channel"
        meanings[101]= " Client reporting measure  on a channel"
        meanings[200]= " Server cmds client to calibrate for a vin on a channel"    
        meanings[201]= " Client reporting on calibration for a vin on a channel"    

stepdict=dict()
stepdict[0]= [3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5]
stepdict[1]=[6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8.0, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 9.0]
stepdict[2] =[9.0, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 11.0, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 12.0, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9, 13.0, 13.1, 13.2, 13.3, 13.4, 13.5]

def timestamp(self):
    '''Returns local time as string, eg: YYYY-mm-DD HH:MM:SS'''
    dt = time.localtime()
    return f'{dt[0]}-{dt[1]}-{dt[2]}  {dt[4]}:{dt[5]}:{dt[6]}.{dt[7]}'

def calibrate(chan, conn):
    ''' This is a test method in db_server to see if we can calibrate all vins in a channel'''
    steps = stepdict[chan]
    for vin in steps:
        obj= {"purpose":200, "chan" : ch, "vin": vin}
        payload= json.dumps(obj)
        time.sleep(2)
      #  input(f" Press return to send msg to server for chan: {chan}, vin: {vin}")
        conn.send(payload.encode(FORMAT))
        print( "sending to client: ", payload)
        
        
    
def handle_client(conn: socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    client_initiated_msgs.clear()
    client_can_respond =False
    connected = True
    while connected:
        header = conn.recv(HEADER).decode(FORMAT)  # blocking line

        if not header:
            continue

        msg_len = int(header)
        msg = conn.recv(msg_len).decode(FORMAT)
        if msg == DISCONNECT_MESSAGE:
            connected = False
            break
        else:
            if msg == '10':
                obj= {"purpose": msg, "cfg_ids": dc.cfg_ids }
                payload = json.dumps(obj)
                conn.send(payload.encode(FORMAT))
            elif msg == '20' :
                obj={"purpose": msg, "chan" : 0, "lut" : dc.luts[0]}
                payload = json.dumps(obj)
                conn.send(payload.encode(FORMAT))
            elif msg == '30' :
                obj={"purpose": msg, "chan" : 1, "lut" : dc.luts[1]}
                payload = json.dumps(obj)
                conn.send(payload.encode(FORMAT))
            elif msg == '40' :
                obj={"purpose": msg, "chan" : 2, "lut" : dc.luts[2]}
                payload = json.dumps(obj)
                conn.send(payload.encode(FORMAT))
            elif msg == '50' :
                client_can_respond=True
                print(f" Client can now respond to Server Cmds:  {client_can_respond}")

            else:   # msg is not just a number...
                # rqsts from someone will be delegated to client to respond
                jsonx = json.loads(msg)
                intent = jsonx['purpose']
        
                if intent == '100': #someone requested a measure
                    #chan= jsonx['chan']
                    #obj={f"purpose" : '100' , "chan":{chan} }
                    #payload=json.dumps(jsonx)
                    conn.send(msg)
                elif intent == '200': # someone requested a calibration
                    #chan = jsonx['chan']
                    #vin = jsonx['vin']
                    #obj={f"purpose" : '200' , "chan":{chan}, "vin" :{vin}}
                    #payload=json.dumps(jsonx)
                    #just send the msg to the client for its response.
                    if client_can_respond:
                        calibrate(0, conn)
                elif intent == '101':
                    print("server received measurement response...")
                    save_measurement(jsonx)
                elif intent == '201':
                    print("201:server received calibration response...")
                    save_calibration(jsonx)

        print(f"[MESSAGE RECEIVED AT SERVER:][{addr}] {msg} ")
    conn.close()
 

# def create_cols_vals(self, jsonx):
#     '''Removes purpose, Returns two lists with column names (cols) and values (vals).'''
#     # db table BMS has no column 'purpose' . ' type'  is used to reflect calibration instead. remove 'purpose' by pop
#     jsonx.pop('purpose')
#     cols=[]
#     vals=[]
#     for k,v in jsonx.items():
#         cols.append(k)
#         vals.append(v)
#     return (cols, vals)

def save_measurement(self, json1):
    ''' request datacontroller to save  a measurement.'''
    json1['type']='m'
    json1['timestamp'] = self.timestamp()
    (cols, vals)=self.create_cols_vals(json1)
    print(f"Called dbsvr.save_measurement() with msg: {json1}")
    dc.save_measurement(json1)

def save_calibration(json1):
    ''' Sets type to calibration ('c'), creates lists for column names (cols) and values (vals).
       Requests datacontroller to save_calibration.'''
    json1['type'] = 'c'
    json1['timestamp'] = self.timestamp()
    print(f"Called dbsvr.save_calibration() with msg: {json1}")
    dc.save_calibration(json1)

                
def start():
    server.listen()
    while True:
        conn, addr = server.accept()  # blocking line
        thread = threading.Thread(target=handle_client, args=(conn, addr))

        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] Server is starting ...")
start()


#  handled under else:
#             elif msg == '200' "
#                 jsonx = json.loads(msg) # this cmd will come from asyncio calls but for now just try it:
#                 intent = jsonx['purpose']
#                 obj={"purpose" : '200' , "chan": 0, "vin" :3.10}
#                 payload=json.dumps(obj)
#                 conn.send(payload.encode(FORMAT))
#          
