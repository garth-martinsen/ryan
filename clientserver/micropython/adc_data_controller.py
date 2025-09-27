# file: adc_data_controller.py

import socket
import json
from adc import ADC
from collections import OrderedDict

CONFIGURING = 0
WORKING = 1
sender_id = "adc_client"

class AdcDataController:
    def __init__(self):
        self.adc=ADC()
        self.mode = CONFIGURING 
        self.cfg_ids=()
        self.configs=[[],[],[]]
        self.luts=[{},{},{}]
        self.rqsts_to_server = [0]
        self.rqsts_from_server = []
        self.respns_from_server = []
        self.respns_by_client = []
        self.msg_id = 3000
        self.next_msg ={1:   {"purpose": 10, "sender_id": "adc_client", "msg_id": self.nextmsgid()},
                        11:  {"purpose": 20, "sender_id": "adc_client", "msg_id": self.nextmsgid()},
                        21: {"purpose": 30, "sender_id": "adc_client", "msg_id": self.nextmsgid()},
                        31: {"purpose": 40, "sender_id": "adc_client", "msg_id": self.nextmsgid()},
                        41: {"purpose": 60, "sender_id": "adc_client", "msg_id": self.nextmsgid()},
                        61:  {"purpose": 50, "sender_id": "adc_client", "msg_id": self.nextmsgid()}    }

    def DISCONNECT_MESSAGE(self):
        return json.dumps( {"purpose": -1, "sender_id": sender_id, "msg_id": -1,"desc": "DISCONNECT"})
        
    def nextmsgid(self):
        self.msg_id+=1
        return self.msg_id
    
    def show_data(self):
        print(f" cfg_ids: {self.cfg_ids}")
        print()
        print("Configs")
        print(f" configs 0: {self.configs[0]}")
        print(f" configs 1: {self.configs[1]} ")
        print(f" configs 2: {self.configs[2]}  ")
        print()
        print(f" Lookup Tables")
        print(f" luts0: {self.luts[0]} ")
        print(f"lut 1: {self.luts[1]} ")
        print(f"lut 2: {self.luts[2]} ")

    def handle_message(self, msg):
        '''Msg is always from server. Check for required fields, then route to configure(...) or handle_task(...).'''
        if self.has_rqd_fields(msg):
             purpose = msg["purpose"]
             sender_id = msg["sender_id"]
             msg_id = ["msg_id"]
             self.respns_from_server.append(purpose)

        if self.mode == CONFIGURING:
            return self.nextconfigure(msg, purpose, sender_id, msg_id)
        elif self.mode == WORKING:
            return self.handle_task(msg, purpose, sender_id, msg_id) 

    def nextconfigure(self, msg, purpose, sender_id, msg_id):
        ''' Check that 3 rqd fields are present. if so, Using purpose from msg lookup response to server. 
         Stringify response and return it to adc_client to send'''
        if purpose < 62:
             response = self.next_msg[purpose]
             self.rqsts_to_server.append(response["purpose"])
        if purpose == 11:
             self.cfg_ids=tuple(msg["cfg_id"])
        if purpose == 21:
             lut = msg["lut"]
             self.luts[0]= OrderedDict(sorted(lut.items()))
        if purpose == 31:
             lut = msg["lut"]
             self.luts[1]= OrderedDict(sorted(lut.items()))
        if purpose == 41:
            lut = msg["lut"]
            self.luts[2]= OrderedDict(sorted(lut.items()))
        if purpose == 51:
           response = {"purpose": 60, "sender_id": "adc_client", "msg_id": self.nextmsgid()}
        if purpose == 61:
           print("purpose: 61  Setting the configs")
           self.configs[0]= msg["config0"]
           self.configs[1]= msg["config1"]
           self.configs[2]= msg["config2"]
           self.mode=WORKING
           response = {"purpose": 52, "sender_id": "adc_client", "msg_id": self.nextmsgid()}
           self.log()
           #self.show_data()
        return json.dumps(response)

    def has_rqd_fields(self, msg):
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


    def handle_task(self, msg, purpose, sender_id, msg_id):
        '''ADC_client is configured and ready... Purpose will be one of: [100, 200].
        The 300 and 400 Tasks are broken down and handled by the server so that Adc_client 
        sees only a 100 or a 200 and returns a 101 or a 201 '''
        if purpose == 100:
            chan = msg["chan"]
            self.rqsts_from_server.append(purpose)
            response = adc.measure(chan)
            response["msg_id"]=self.nextmsgid()
            response["sender_id"]=sender_id
            response["purpose"]=101
            self.respns_by_client.append(101)

        elif purpose == 200:
             chan = msg["chan"]
             vin = msg["vin"]             
             self.rqsts_from_server.append(purpose)
             response = adc.calibrate(chan, vin)
             response["msg_id"]=self.nextmsgid()
             response["msg_id"]=self.nextmsgid()
             response["sender_id"]=sender_id
             response["purpose"]=201
             self.respns_by_client.append(201)
        else:
            print("Error. Adc_client in WORKING mode should receive only msgs with purpose: 100 or 200 ." )

        
    def greet_and_register(self):
        ''' sends msg with purpose=0 with sender_id, so server knows socket for adc_client.'''
        obj = {"purpose": 0, "sender_id": "adc_client", "msg_id": self.nextmsgid()}   
        return json.dumps(obj)

    def disconnect(self):
        return self.DISCONNECT_MESSAGE()

    def log(self):
        print()
        print("Log of client-server traffic since client startup:")
        print("rqsts_to_server: ", self.rqsts_to_server)
        print("respns_from_server:        ", self.respns_from_server)
        print("rqsts_from_server: ", self.rqsts_from_server)
        print("respns_from_Client: ", self.respns_by_client)
        print()
        print("AdcDataController.data ...")
        self.show_data()
                      


