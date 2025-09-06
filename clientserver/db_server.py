# file db_server.py  from simplifed version: /Users/garth/DIST/clientserver/ryan/learn/myserver2.py  8/23/2025
# copied from: https://github.com/juliogema/python-basic-socket/blob/main/server.py
# to clear locked ip address:  lsof +c 0 -i:5050 -n  Then kill pid that shows up.

import threading
import socket
import json
from data_controller import DataController

HEADER = 64  # bit
PORT = 5050
#SERVER = '192.168.254.19'  #change according to the ipaddress of your host.
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE =  "!DISCONNECTED"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

#global vars which change upon the receipt of each client msg.
msg=''
adc_conn = None
gui_conn  = None
sender_id = 'server'


class  db_server:
    def __init__(self): 
        self.dc = DataController((1,2,3))  # initialize with your project's cfg_ids here instead of (1,2,3)
        self.clients_READY               = dict()
        #self.sockets_by_addr             = dict()
        #self.client_names_by_addr   = dict()
        self.responses_per_rqst        = dict()
        self.load_responses()            # loads the responses_per_rqst dict
        self.msgs_for_gui_client         = []
        self.msgs_for_adc_client        = []

    def load_responses(self):
        '''As server receives msgs, the purpose is extracted and actions are performed. this dict returns the response msg'''
        # 0 < purpose <99 are returned to sender for both clients
        # for 100 <= purpose <= 500 : save data to db and forward to the other client
        #self.responses_per_rqst = dict()
        #self.responses_per_rqst[0]   = {"purpose":1, "greet": "Welcome!"}
        self.responses_per_rqst[10] = {"purpose":11, "sender_id":sender_id,"cfg_ids": tuple(self.dc.cfg_ids)}
        self.responses_per_rqst[20] = {"purpose":21, "sender_id":sender_id, "chan":0, "lut": self.dc.luts[0]}
        self.responses_per_rqst[30] = {"purpose":31,  "sender_id":sender_id,"chan":1, "lut":  self.dc.luts[1]}
        self.responses_per_rqst[40] = {"purpose":41,  "sender_id":sender_id, "chan":2, "lut":  self.dc.luts[2]}
        self.responses_per_rqst[50] = {"purpose":51,  "sender_id":sender_id,"status": self.clients_READY }
        self.responses_per_rqst[60] = {"purpose":61,  "sender_id":sender_id, "config": self.dc.cfg }

    def send_lut(self, purpose, chan, lut):
        global msg, conn, addr
        obj= { "purpose": purpose,  "sender_id": sender_id, "chan":chan, "lut": lut}
        msg=json.dumps(obj)
        #print(f"msg: {msg}")
        conn.send(msg)
        
    def update_READY(self):
        global msg, addr, conn
        if addr:
            client_name= self.client_names_by_addr[addr]
            socket = self.sockets_by_addr[addr]
                                                        
    def save_to_database(self,  purpose):
        '''Msg sent by adc_client. Has bms in msg. Save to database . Already forwarded to gui_client.'''
        global msg, conn, addr 
        if msg and conn and addr:
            bms = msg['bms']
            rspns = dbs.responses_per_rqst[purpose]
            # save bms to database
            print(f" saving  to database  bms: {bms}")
            if purpose == 101:
                dbs.dc.save_measurement(bms)
            elif purpose ==201:
                dbs.dc.save_calibration(bms)   

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# socket method...
def handle_client(conn: socket, addr):
    global adc_conn, gui_conn
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True

    while connected:
        header = conn.recv(HEADER).decode(FORMAT)  # connecting blocking line===========
        #print(f" while connected: header: {header}")
        if not header:
            continue
        msg_len = int(len(header))
        amsg = conn.recv(msg_len).decode(FORMAT)     # incoming msg  blocking line =============
        
        if amsg ==  DISCONNECT_MESSAGE:
            connected = False
            break
        
       #print(f" msg received at server: {amsg}")
       # turn string into dict using json and get purpose and sender from the msg
        msg= json.loads(amsg)
        purpose = int(msg["purpose"])
        sender_id = msg["sender_id"]
        if sender_id == 'adc_client':
            adc_conn = conn
        else:
            gui_conn = conn
        #print(f" conn:  {conn}  adc_conn: {adc_conn}  gui_conn: {gui_conn}")
        if purpose == 0:
            sender_id= msg["sender_id"]
            rspns ={"purpose": 1, "greet": "Svr welcomes ", "sender_id" :  sender_id }
            rmsg = json.dumps(rspns)
            #print(f" type: {type(rmsg)}   rmsg: {rmsg}")
            conn.send(rmsg.encode(FORMAT))
        # execute the correct action given the purpose...    
        print(f"\n[MESSAGE RECEIVED][{addr}] {msg} ")
        print(f" preparing msg : {purpose+1 }  to respond to msg : {purpose}")
        if 0 < purpose < 60:
            rspns = json.dumps(dbs.responses_per_rqst[purpose])   # given rqst with purpose, returns rspns ( purpose+1)
            conn.send(rspns.encode(FORMAT))
        elif purpose == 60:
            obj = {"purpose": 61, "sender_id": sender_id, "configs0" : dbs.dc.cfg[0][:-1], "configs1": dbs.dc.cfg[1][:-1], "configs2": dbs.dc.cfg[2][:-1]}
            rmsg = json.dumps(obj)
            conn.send(rmsg.encode(FORMAT))
        if purpose in [100,200]  and sender_id == 'gui_client':
            # purpose x00 is coming from gui_client.. put it into msgs_for_adc_client...
            dbs.msgs_for_adc_client.append(msg)
            print(f"msgs_for_adc_client : {dbs.msgs_for_adc_client}")
            # if there are any msgs for gui, pop and send while its conn is in active thread.
            if dbs.msgs_for_gui_client :
                gui_msg = dbs.msgs_for_gui_client.pop()
                conn.send(gui_msg)
        if purpose in [101, 201] and sender_id == 'adc_client':
            # purpose x01 is coming from adc_client... put msg into msgs_for_gui_client...
            dbs.save_to_database( purpose, msg)
            dbs.msgs_for_gui_client.append(msg)
            print(f"msgs_for_gui_client : {dbs.msgs_for_gui_client}")
            # if there are any msgs for adc, pop and send.
            if dbs.msgs_for_adc_client :
                adc_msg = dbs.msgs_for_adc_client.pop()
                conn.send(adc_msg)
            
#socket method...
def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()  # blocking line
        thread = threading.Thread(target=handle_client, args=(conn, addr))

        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

# --------- calls ------------------
dbs = db_server()

print("[STARTING] Server is starting ...")

start()

