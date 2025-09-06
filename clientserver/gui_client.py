# file: gui_client.py    purpose: liason between gui and adc_client thru db_server. runs in python3 env.
# copied and modified:  https://github.com/juliogema/python-basic-socket/blob/main/client.py
# Notes: For each server response, only one client request can be made eg: on purpose:11 can send request(20)
# TODO 2: Find out why the request to measure(0) from gui_client causes problems.


import socket
import json
from collections import OrderedDict

"""adc_client  Configuration includes [10,20,30,40,50]  50 tells server that adc_client is READY
... Use the same and add request(60) for config records for gui_client. Following the response for 60, send requests: 
100: measure(chan)
200: calibrate(chan, vin)
300: repeating measurement sequence includes [3 measure(chan), 1 wait].  Future...
400: repeating calibration sequence includes 3 sets of stepping vins with. delay to set Power supply. Future..."""
# =======client code=========
HEADER = 64
PORT = 5050
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.254.19"
ADDR = (SERVER, PORT)

# globals
svr_msgs_cnt = 0
resps_from_svr = []
rqsts_to_svr = []
sender_id= 'gui_client'

class gui_data:
    def __init__(self):
        self.client_name = "gui_client"
        self.cfg_ids = ()
        self.luts = [{}, {}, {}]
        self.configs = [[], [], []]  # all fields in CONFIG table (except luts)
        self.measurements = []  # all records from BMS table where type='m'
        self.calibrations = []  # all records from BMS table where type='c'

    def show_gui_data(self):
        print(f" client: {self.client_name} ")
        print()
        print(f" cfg_ids: {self.cfg_ids} ")
        print("*************Configuration:************")
        print(f" configuration[0] : {self.configs[0]}")
        print()
        print(f" configuration[1] : {self.configs[1]}")
        print()
        print(f" configuration[2] : {self.configs[2]}")
        print()
        print("************Lookup tables:***********")
        print(f"Lookup table 0: {self.luts[0]}")
        print()
        print(f"Lookup table 1: {self.luts[1]}")
        print()
        print(f"Lookup table 2: {self.luts[2]}")
        print()
        print("************Measurements***********")
        print(f" measurements [0]: {self.measurements}")
        print("************Calibrations***********")
        print(f" calibrations: {self.calibrations}")


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def send(msg):
    global svr_msgs_cnt, resps_from_svr, rqsts_to_svr
    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_length = str(msg_len).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))

    client.send(send_length)
    client.send(message)
    # receive msg from server========blocking method =============
    while True:
        amsg = client.recv(2024)
        svr_msgs_cnt += 1
        # print(f"amsg in client.recv(): {amsg} ")
        if amsg:
            msg = json.loads(amsg)
            # print(f" type: {type(msg)} msg: {msg} ")
            purpose = msg["purpose"]
            sender_id = msg["sender_id"]
            resps_from_svr.append(purpose)
            # TODO: Decide if every msg should have sender_id field. Causing error here.
            # take action depending on purpose...
            if purpose in [0, 1]:
                sender_id = msg["sender_id"]
                gui_data.client_name = sender_id
                request(10)
            elif purpose == 11:
                gui_data.cfg_ids = tuple(msg["cfg_ids"])
                request(20)
                # TODO: for each response from the server, only one more request can be made..
            elif purpose == 21:
                chan = msg["chan"]
                lut = msg["lut"]
                gui_data.luts[chan] = convert_to_dict(lut)
                request(30)
            elif purpose == 31:
                chan = msg["chan"]
                lut = msg["lut"]
                gui_data.luts[chan] = convert_to_dict(lut)
                request(40)
            elif purpose == 41:
                chan = msg["chan"]
                lut = msg["lut"]
                gui_data.luts[chan] = convert_to_dict(lut)
                send_ready()
            elif purpose == 51:
                request(60)
            elif purpose == 61:
                gui_data.configs[0] = msg["configs0"]
                gui_data.configs[1] = msg["configs1"]
                gui_data.configs[2] = msg["configs2"]
                chan = 0
                rqst_measure(chan)
            elif purpose in [100,200]:
                print("Error! This msg should not be here. It should have been routed to adc_client.")
            elif purpose == 101:
                print(f" msg forwarded from adc by server: {msg}")
                chan = 0
                vin = 3.6
                rqst_calibration(chan, vin)
            elif purpose == 201:
                print(f" msg forwarded from adc by server: {msg}")
                log()


# definitions for gui_client calls to server...
def hi():
    obj = {"purpose": 0, "sender_id": sender_id}  
    msg = json.dumps(obj)
    #print(f" in hi(), type: {type(msg)}  msg for hi: {msg}")
    rqsts_to_svr.append(0)
    send(msg)


def send_ready():
    obj = {"purpose": 50, "sender_id": "gui_client"}  # gui_client is a literal string
    msg = json.dumps(obj)
    rqsts_to_svr.append(50)
    send(msg)


def request(num):
    global sender_id
    obj = {"purpose": num, "sender_id": sender_id}
    msg = json.dumps(obj)
    rqsts_to_svr.append(num)
    send(msg)
    return

def convert_to_dict(lut):
    """create dict to return for assignment to adc. works for all channels"""
    lutx = {}
    for k, v in lut.items():
        lutx[float(k)] = v
    return OrderedDict(sorted(lutx.items()))

def disconnect():
    send(DISCONNECT_MESSAGE)

def rqst_measure(chan):
    global sender_id
    rqsts_to_svr.append(100)
    obj = {"purpose": 100,"sender_id": sender_id, "chan": chan}
    msg = json.dumps(obj)
    send(msg)


def rqst_calibration(chan, vin):
    global sender_id
    rqsts_to_svr.append(200)
    obj = {"purpose": 200, "sender_id": sender_id, "chan": chan, "vin": vin}
    msg = json.dumps(obj)
    send(msg)


def log():
    gui_data.show_gui_data()
    print()
    print(f"requests_to_server:            {rqsts_to_svr} ")
    print(f"responses_from_server:     {resps_from_svr} ")
    print(f"server msgs_count:             {svr_msgs_cnt}")


# called methods-----
gui_data = gui_data()
hi()
