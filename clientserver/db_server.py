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
conn=None
addr=None

class  db_server:
    def __init__(self): 
        self.dc = DataController((1,2,3))  # initialize with your project's cfg_ids here instead of (1,2,3)
        self.clients_READY               = dict()
        self.sockets_by_addr             = dict()
        self.client_names_by_addr   = dict()
        self.rsps_per_rqst                  = dict()
        self.load_rsps()                      # a dict

    def load_rsps(self):
        '''As server receives msgs, the purpose is extracted and actions are performed. this dict returns the response msg'''
        # 0 < purpose <99 are returned to sender for both clients
        # for 100 <= purpose <= 500 : save data to db and forward to the other client
        #self.rsps_per_rqst = dict()
        self.rsps_per_rqst[0]   = {"purpose":1, "greet": "Welcome!"}
        self.rsps_per_rqst[10] = {"purpose":11, "cfg_ids": tuple(self.dc.cfg_ids)}
        self.rsps_per_rqst[20] = {"purpose":21, "chan":0, "lut": self.dc.luts[0]}
        self.rsps_per_rqst[30] = {"purpose":31, "chan":1, "lut":  self.dc.luts[1]}
        self.rsps_per_rqst[40] = {"purpose":41, "chan":2, "lut":  self.dc.luts[2]}
        self.rsps_per_rqst[50] = {"purpose":51, "status": self.clients_READY  }
        self.rsps_per_rqst[100]= {"purpose":100,  "status": "forward msg to adc_client" }            # gui_client -> dbs, then fwd to :  adc_client
        self.rsps_per_rqst[200]= {"purpose":200,  "status": "forward msg to adc_client"  }             # gui_client -> dbs, then fwd to :  adc_client
        self.rsps_per_rqst[101]= {"purpose":101, "status": "save data and forward to gui_client" }   # adc_client -> dbs->dbi, then fwd to :  gui_client
        self.rsps_per_rqst[201]= {"purpose":201, "status": "save data and forward to gui_client" }   # adc_client -> dbs->dbi, then fwd to :  gui_client

    def acknowlege_client(self):
         '''Responding to 0:connect and introduce. Create and send back a welcome msg. '''
         global msg, conn, addr
         obj =f' {"purpose": 1, "load": "Hello. Welcome aboard {addr}!."}'
         msg=json.dumps(obj)
         print(f"msg: {msg}")
         conn.send(msg)
    
    def send_lut(self, purpose, chan, lut):
        global msg, conn, addr
        obj= f'purpose": {purpose}, "chan":chan, "lut": lut'
        msg=json.dumps(obj)
        print(f"msg: {msg}")
        conn.send(msg)
        
    def the_other_socket(self, conn, addr):
        ''' (conn, addr) is from active client. Returns the other client_name and other_socket'''
        if len(self.sockets_by_addr) < 2:  #only one socket in dict
            other_client = other_socket = None
            print(f"Only one client has connected so other_client: {other_client}  and other_socket: {other_socket}")
        else:
            sockets= set (self.sockets_by_addr.keys())
            other = sockets.difference({addr}).pop()  # other is an addr (string)
            other_client_name  = self.client_names_by_addr[other]  #other_client is name of client, a string
            other_socket = self.sockets_by_addr[other]       # other_socket is a socket
            print(f" other_client : {other_client_name} ")
            print(*f" other_socket: {other_socket} ")
        return (other_client_name, other_socket)
    
    def update_READY(self):
        global msg, addr, conn
        if addr:
            client_name= self.client_names_by_addr[addr]
            socket = self.sockets_by_addr[addr]
                                        
    def forward_to_adc_client(self, purpose):
        ''' msg is from gui_client. Forward msg to adc_client'''
        global msg, addr, conn
        if len(self.sockets_by_addr) > 1 and  msg and conn and addr:
            adc_client, adc_socket = self.the_other_socket(conn, addr)
            cmd = json.dumps(msg)
            print(f" sending {cmd}  to {adc_client} on socket: {adc_socket}")
            adc_socket.send(cmd.encode(FORMAT))
        else:
            print("Only one socket in sockets_by_addr. Wait for other client to connect...")
                
    def save_and_forward_to_gui_client(self, purpose):
        '''Msg sent by adc_client. Has bms in msg. Save to database then forward to gui_client.'''
        global msg, conn, addr 
        if msg and conn and addr:
            bms = msg['bms']
            print(f" BMS: {bms}")
            rspns = dbs.rsps_per_rqst[purpose]
            print("Finish the code in save and forward_to_gui_client()")
            dbs.dc.save_bms(bms)
            gui_client, gui_socket = self.the_other_socket(self, conn, addr)
            cmd = json.dumps(msg)
            gui.socket.send(cmd.encode(FORMAT))
    

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


# socket method...
def handle_client(conn1: socket, addr1):
    global msg, conn, addr
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    conn=conn1
    addr = addr1
    while connected:
        header = conn.recv(HEADER).decode(FORMAT)  # blocking line===========
        if not header:
            continue
        # print(f" header: {header}")
        msg_len = int(header)
        amsg = conn.recv(msg_len).decode(FORMAT)     # blocking line =============
        
        if amsg ==  DISCONNECT_MESSAGE:
            connected = False
            break
        
       #print(f" msg received at server: {amsg}")
       # turn string into dict using json and get info from the msg
        msg= json.loads(amsg)
        purpose = int(msg["purpose"])
        if purpose == 0:
            client_id= msg["client_id"]
            dbs.client_names_by_addr[addr]=client_id
            dbs.sockets_by_addr[addr]=conn
            rspns ={"purpose": 1, "greet": f"Svr says welcome {client_id}", "client_id": client_id}
            rmsg = json.dumps(rspns)
            conn.send(rmsg.encode(FORMAT))
        # execute the correct action given the purpose...    
        print(f"\n[MESSAGE RECEIVED][{addr}] {msg} ")
        print(f" sending msg : {purpose+1 }  responding to msg : {purpose}")
        #print(f"actions: {dbs.rsps_per_rqst}")
        #print(f"          client_names: {dbs.client_names_by_addr}  \n          sockets: {dbs.sockets_by_addr}\n")
        
        #obj={"purpose": purpose + 1, "load": dbs.acts_per_purpose[purpose]}
      
        if 5 < purpose < 100:
            rspns = json.dumps(dbs.rsps_per_rqst[purpose])   # given rqst with purpose, returns rspns ( purpose+1)
            conn.send(rspns.encode(FORMAT))
        elif purpose in [100,200] :
            dbs.forward_to_adc_client(purpose)            
            conn.send(rspns.encode(FORMAT))
        elif purpose in [101, 201]:
            dbs.save_and_forward_to_gui_client(purpose)
            
    conn.close()   
    conn1.close()
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
dbs.load_rsps()
print("[STARTING] Server is starting ...")
start()

