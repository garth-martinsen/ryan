# file: adc_data_controller.py

import socket
import json
from adc import ADC
from collections import OrderedDict

CONFIGURING = 0
WORKING = 1
sender_id = "adc_client"


class AdcDataController:
    def __init__(self, cfg_ids):
        self.mode = CONFIGURING
        #self.cfg_ids =cfg_ids
        #self.configs = [ [], [], [] ]
        #self.luts = [{}, {}, {}]
        self.rqsts_to_server = [0]
        self.rqsts_from_server = []
        self.respns_from_server = []
        self.respns_by_client = []
        self.msg_id = 4000
        self.adc = ADC()
        self.next_msg = {
            1: {"purpose": 10, "sender_id": "adc_client", "msg_id": self.nextmsgid()},
            11: {"purpose": 12, "sender_id": "adc_client", "msg_id": self.nextmsgid()},
            13: {"purpose": 14, "sender_id": "adc_client", "msg_id": self.nextmsgid()},
            15: {"purpose": 50, "sender_id": "adc_client", "msg_id": self.nextmsgid()}
             }

    def handle_message(self, msg):
        '''Msg is always from server. Check for required fields, then route to nextconfigure(...) or handle_task(...). If response
has already been received, do not send a msg back to server...'''
        print(f"adc.handle_message(...) type(msg): {type(msg)}")
        if self.has_rqd_fields(msg):
            purpose = msg["purpose"]
            sender_id = msg["sender_id"]
            msg_id = ["msg_id"]
            #avoid endless loop. In adc_client, do not send(message) if it is None
            if purpose in self.respns_by_client:
                return None
            self.respns_from_server.append(purpose)
        if self.mode == CONFIGURING:
            return self.nextconfigure(msg, purpose, sender_id, msg_id)
        elif self.mode == WORKING:
            return self.handle_task(msg, purpose, sender_id, msg_id)

    def kill_process(self):
        ''' kills the process with the name: "Python db_server.py"  '''
        import os, signal
        name ="Python db_server.py"
        try:
            # iterating through each instance of the process
            for line in os.popen("ps ax | grep " + name + " | grep -v grep"): 
                fields = line.split()
                # extracting Process ID from the output
                pid = fields[0]
                # terminating process 
                os.kill(int(pid), signal.SIGKILL) 
            print("Process Successfully terminated")
        
        except:
            print("Error Encountered while running script")
            
    def DISCONNECT_MESSAGE(self):
        return json.dumps(
            {"purpose": -1, "sender_id": sender_id, "msg_id": -1, "desc": "DISCONNECT"}
        )

    def nextmsgid(self):
        self.msg_id += 1
        return self.msg_id

    def show_data(self):
        print(f" cfg_ids: {self.cfg_ids}")
        print()
        print("Configs")
        print(f" adc.configs 0: {self.adc.configs[0]}")
        print(f" adc.configs 1: {self.adc.configs[1]} ")
        print(f" adc.configs 2: {self.adc.configs[2]}  ")
        print()
        print(f" Lookup Tables")
        print()
        print(f" luts0: {self.luts[0]} ")
        print()
        print(f"lut 1: {self.luts[1]} ")
        print()
        print(f"lut 2: {self.luts[2]} ")
        print("==================")

   
    def nextconfigure(self, msg, purpose, sender_id, msg_id):
        """Check that 3 rqd fields are present. if so, Using purpose from msg lookup response to server.
        Stringify response and return it to adc_client to send"""
        if purpose == 1:
            response = self.next_msg[purpose]
            self.rqsts_to_server.append(response["purpose"])
        if purpose == 11:
            print("Using cfgs from msg 11 to set self.adc.configs[0]... sending msg 12")
            self.adc.configs[0]= msg["cfg0"]
            self.adc.luts[0] = self.adc.configs[0][-1]
            self.adc.configs[0]= self.adc.configs[0][:-1]
            response = self.next_msg[11]
            self.rqsts_to_server.append(response["purpose"])
        if purpose == 13:
            print("Using cfg1 from msg 13 to set self.configs[1] and luts[1]...sending msg 14")
            self.adc.configs[1]= msg["cfg1"]
            self.adc.luts[1] = self.adc.configs[1][-1]
            self.adc.configs[1]= self.adc.configs[1][:-1]
            response = self.next_msg[13]
            self.rqsts_to_server.append(response["purpose"])
        if purpose == 15:
            print("Using cfg1 from msg 13 to set self.configs[1] and luts[1]...sending 14")
            self.adc.configs[2]= msg["cfg2"]
            self.adc.luts[2] = self.adc.configs[2][-1]
            self.adc.configs[2]= self.adc.configs[2][:-1]
            # set cfg_ids
            cfg_id1 = self.adc.configs[0][0]
            cfg_id2 = self.adc.configs[1][0]
            cfg_id3 = self.adc.configs[2][0]
            self.adc.cfg_ids = (cfg_id1, cfg_id2, cfg_id3)
            print("cfg_ids: ", self.adc.cfg_ids)
            print("configs: ", self.adc.configs)
            print("luts: ", self.adc.luts)
            response = self.next_msg[15]
            self.rqsts_to_server.append(response["purpose"])

        if purpose == 51:
            self.mode = WORKING
            response = None
        if purpose != 51:
            return response

    def has_rqd_fields(self, msg):
        """Every message must have 3 fields: purpose, sender_id, and msg_id, then other fields as needed."""
        p = s = m = True
        if "purpose" not in msg:
            print("Each msg must have field:  purpose ")
            p = False
        if "sender_id" not in msg:
            print("Each msg must have a field: sender_id")
            s = False
        if "msg_id" not in msg:
            print("Each msg must have a field: msg_id")
            m = False
        return p and s and m

    def handle_task(self, msg, purpose, sender_id, msg_id):
        """ADC_client is configured and ready... Purpose will be one of: [100, 200].
        The 150 and 250 Tasks are broken down and handled by the server so that Adc_client
        sees only a 100 or a 200 and returns a 101 or a 201"""
        if purpose == 100:
            chan = msg["chan"]
            self.rqsts_from_server.append(purpose)
            response = adc.measure(chan)             #action
            response["msg_id"] = self.nextmsgid()
            response["sender_id"] = sender_id
            response["purpose"] = 101
            self.respns_by_client.append(101)
            self.log()

        elif purpose == 200:
            chan = msg["chan"]
            vin = msg["vin"]
            self.rqsts_from_server.append(purpose)
            response = adc.calibrate(chan, vin)
            response["msg_id"] = self.nextmsgid()
            response["msg_id"] = self.nextmsgid()
            response["sender_id"] = sender_id
            response["purpose"] = 201
            self.respns_by_client.append(201)
            self.log()
        elif purpose == 151:
            #TODO li 169 : schedule_measurements
            print(f" schedule Measurements is TBD li:170 msg: {msg}" )
        elif purpose == 175 :
            print(f" fetch Measurements is TBD li:172 msg: {msg}" )
            #TODO li 173 : fetch measurements
        elif purpose == 251:
            print(f" stepping calibrations TBD li:175  msg: {msg}" )
            #TODO li 176 : stepping calibrations 
        elif purpose == 275 :
            print(f" fetch calibrations TBD li:178  msg: {msg}" )
            #TODO li 179 :  fetch calibrations
        else:
           print( "Error. Adc_data_controller  in WORKING mode should receive only msgs with purposes: 100 | 151 |175 | 200 | 251 | 275 " )
           print(msg)

    def greet_and_register(self):
        """sends msg with purpose=0 with sender_id, so server knows socket for adc_client."""
        obj = {"purpose": 0, "sender_id": "adc_client", "msg_id": self.nextmsgid()}
        return json.dumps(obj)

    def configure(self):
        """sends msg with purpose=10 with sender_id=adc_client, so server returns configs."""
        obj = {"purpose": 10, "sender_id": "adc_client", "msg_id": self.nextmsgid()}
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
