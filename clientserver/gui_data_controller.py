# file:  gui_data_controller.py  #data handler in the gui_client.py

import json
from copy import deepcopy



DISCONNECT_MESSAGE = json.dumps(
    {"purpose": -1, "sender_id": "gui_client", "desc": "DISCONNECT"}
)


class GuiDataController:
    def __init__(self, cfg_ids):
        self.client_name = "gui_client"
        self.cfg_ids = cfg_ids
        self.luts = [{}, {}, {}]
        self.configs = [[], [], []]  # all fields in CONFIG table (except luts)
        self.status = 'Pending'
        self.measurements = [[], [],[] ]  # all records from BMS table where type='m'
        self.calibrations = [[],[],[]]  # all records from BMS table where type='c'
        self.rqsts_to_svr=[]
        self.resps_from_svr=[]
        self.svr_msgs_cnt=0
        self.msg_start =  {"purpose": 0, "sender_id": "gui_client", "msg_id": -99}
        self.msg_id = 6000     #starting msg_id in gui_data_controller...
        self.responses_for_purpose = {1:   {"purpose": 10, "sender_id": "gui_client", "msg_id": self.nextmsgid()},
         11:  {"purpose": 20, "sender_id": "gui_client", "msg_id": self.nextmsgid()},
         21: {"purpose": 30, "sender_id": "gui_client", "msg_id": self.nextmsgid()},
         31: {"purpose": 40, "sender_id": "gui_client", "msg_id": self.nextmsgid()},
         41: {"purpose": 60, "sender_id": "gui_client", "msg_id": self.nextmsgid()},
         61:  {"purpose": 50, "sender_id": "gui_client", "msg_id": self.nextmsgid()},}
         
        
    def nextmsgid(self):
        '''get the next msg_id  by incrementing by 1 and returning the result.'''
        self.msg_id +=1
        return self.msg_id
   
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
        for chan in range(0,3):
            print(f" measurements {chan}: {self.measurements[chan]}")
        print("************Calibrations***********")
        for chan in range(0,3):
            print(f" calibrations {chan}: {self.calibrations[chan]}")

    def handle_message(self, msg):
        #print("Called gdc.handle_message(...)")
        purpose=-2
        sender_id=''
        msgid=''
        if self.has_rqrd_fields(msg):
            purpose = msg["purpose"]
            sender_id=msg["sender_id"]
            msgid = msg["msg_id"]
            print ("msg: ",msg, " p: ",purpose, " s: ", sender_id, " m: ",msgid )
            if purpose !=51:
                obj = self.responses_for_purpose[purpose]
            else:
                obj={}
            if purpose == 1:
                print( "Recognized and registered with server")
            if purpose == 11:
                cfg_ids = msg["cfg_id"] 
                self.cfg_ids = tuple(cfg_ids)  # should be tuple triplet
                print("self.cfg_ids : ", self.cfg_ids)
            if purpose == 21:
                self.luts[0]= msg["lut"]
            if purpose == 31:
                self.luts[1]= msg["lut"]
            if purpose == 41:
                self.luts[2]= msg["lut"]
            if purpose == 51:
                print("Wait for requests  from FLET GUI to measure, calibrate, schedule, step_calibrate")
            if purpose == 61:
                self.configs[0]= msg["config0"]
                self.configs[1]= msg["config1"]
                self.configs[2] = msg["config2"]
            if purpose == 51:
                print("status: " ,msg["status"])
                self.status = 'READY'
            if obj:
                return json.dumps(obj)

#                   return False  # TODO 8: Figure out how to deal with on demand stuff.
        
    def has_rqrd_fields(self, msg):
        '''Every message must have 3 fields: purpose, sender_id, and msg_id, then other fields as needed.'''
        p=s=m=True
        if "purpose" not in msg:
            print( "Each msg must have field:  purpose ")
            p = False
        if "sender_id" not in msg:
            print("Each msg must have a field: sender_id")
            s=False
        if "msg_id" not in msg:
            print("Each msg must have a field: msg_id")
            m=False
        return p and s and m
  
    # definitions for gui_client calls to server...
    def hi(self):
        '''introduction to the server, so svr can collect sockets for its use'''
        msg_id = self.nextmsgid()
        obj = {"purpose": 0, "sender_id": "gui_client", "msg_id": msg_id}
        msg = json.dumps(obj)
        # print(f" in hi(), type: {type(msg)}  msg for hi: {msg}")
        self.rqsts_to_svr.append(0)
        return msg


    def bye(self):
        '''Sends DISCONNECT_MESSAGE to server'''
        msg = DISCONNECT_MESSAGE
        self.rqsts_to_svr.append(-1)
        return msg


    def send_ready(self,purpose):
        obj = {"purpose": purpose, "sender_id": "gui_client", "msg_id": self.nextmsgid()}  # gui_client is a literal string
        msg = json.dumps(obj)
        rqsts_to_svr.append(purpose)
        return msg


    def request(self, num):
        """num could be any purpose between 2 and 99. Return message is Always  sent back to the sender."""
        msg_id = nextmsgid()
        obj = {"purpose": num, "sender_id": "gui_client","msg_id": msg_id}
        msg = json.dumps(obj)
        rqsts_to_svr.append(num)
        return msg

    def convert_to_dict(self, lut):
        """create dict to return for assignment to data. works for all channels"""
        lutx = {}
        for k, v in lut.items():
            lutx[float(k)] = v
        return OrderedDict(sorted(lutx.items()))

    def rqst_measure(self, chan):
        self.rqsts_to_svr.append(100)
        print(f"Called rqst_measure on chan: {chan}")
        obj = {"purpose": 100, "sender_id": "gui_client", "msg_id": self.nextmsgid(),"chan": chan}
        msg = json.dumps(obj)
        return msg


    def rqst_calibration(self, chan, vin):
        '''msg requests a calibration on a chan for a vin.'''
        global sender_id
        rqsts_to_svr.append(200)
        print(f"Called rqst_calibration on chan: {chan} with vin: {vin}")
        obj = {"purpose": 200, "sender_id": "gui_client",  "msg_id": self.nextmsgid(), "chan": chan, "vin": vin}
        msg = json.dumps(obj)
        return msg


    def log(self):
        self.show_gui_data()
        print()
        print(f"gui_client requests_to_server:                 {self.rqsts_to_svr} ")
        print(f"responses_to_gui_client from_server:     {self.resps_from_svr} ")
        print(f"server msgs_received by_gui_client count:  {self.svr_msgs_cnt}")
        print(f"msg_id: {self.msg_id}")
        



'''
                 chan = 0
                rqst_measure(chan)   # request 100 measure on chan
            elif purpose in [100, 200]:
                print(
                    "Error! This msg should not be here. It should have been routed to adc_client."
                )
            elif purpose == 101:
                print(f" msg from adc forwarded to gui_client by server: {msg}")
                chan = msg["chan"]
                #gui_data.measurements[chan] = msg
                #TODO 5 : Finish filling in measurements correctly...
                #next request
                chan = 0
                vin = float(input("Enter value of vin  "))
                rqst_calibration(chan, vin)  # request calibration on chan with vin
            elif purpose == 201:
                print(f" msg forwarded from adc by server: {msg}")
                 #TODO 6 : Finish filling in calibrations correctly...
                 '''