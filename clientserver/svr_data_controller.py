#file svr_data_controller.py copied from DIST/learn/svr_data_controller_0922.py on 9/27/2025
import time
import ast
import json
from data_controller_config import Lut_Limits, lsb, circuits
from database_interface import DatabaseInterface, BMS
from collections import OrderedDict

class SvrDataController:
    def __init__(self, cfg_ids):
        self.cfg_ids = cfg_ids
        self.cfg = []  # cfg will hold 3 channels of dict [0,1,2]
        self.luts = [ {}, {}, {} ]  # lut will hold 3 Dictionaries: lut42, lut84 and lut126
        self.lut_limits = {}  # dict {channel: lut_limits} channels are: 0,1,2
        self.dbi = DatabaseInterface()
        self.lsb = 4.095 / pow(2, 15)  # ~ 125 µvolts
        self.start_msg = '{"purpose": 0, "sender_id": "server", "msg_id": self.msg_id}'
        self.msg_id = 5000
        self.load_config(self.cfg_ids)
        self.messages_for_adc = []
        self.messages_for_gui=[]

    def load_config(self, ids):
        """Loads db records with ids. Converts Luts to {float:float } and sets limits to iteration.
        This method loads Calibrate View."""
        self.cfg_ids = ids
        self.cfg = self.dbi.load_config(ids)
        for i in range(3):
            self.convert_lut(self.luts[i], i)

    def _limit_lut(self, channel):
        """checks if lut has data, if so it sorts the keys and selects alut[0] for lower and alut[-1]  for upper."""
        alut = OrderedDict(sorted(self.luts[channel].items()))
        #print("alut: ", alut)
        if len(alut) > 1:
            ord_keys = list(alut.keys())
            vm_low = ord_keys[0]
            vb_low = alut[vm_low]
            vm_high = ord_keys[-1]
            vb_high = alut[vm_high]
            # print("Lower Limit: ", lower_limit)
            # print("Upper Limit: ", upper_limit)
            length = (
                len(alut) - 1
            )  # stopping value for row_id, prevents out of bounds on list error
            self.lut_limits[channel] = Lut_Limits(
                circuits[channel], vm_low, vb_low, vm_high, vb_high, length
            )
            print(f"voltage limits to lut {circuits[channel]} are set.")

    def convert_lut(self, lut, channel):
        """LUT from the db fetch is a dict {str:float}, change keys so: dict{float:float }
        and store in memory for lookup use."""
        lut = self.luts[channel]
        lutdict = ast.literal_eval(self.cfg[channel].LUT)
        # lutdict = json.load(self.cfg[channel].LUT)
        # make lutdict a dict{float:float} and store it in proper place
        for k, v in lutdict.items():
            lut[float(k)] = v
        self._limit_lut(channel)

        
    def nextmsgid(self):
        self.msg_id +=1
        return self.msg_id
    
    def missing_rqrd_fields(self,msg):
        if "purpose" not in msg:
            print("missing required field: purpose")
        if "sender_id" not in msg:
            print("missing required field:sender_id")
        if "msg_id" not in msg:
            print("missing required field: msg_id")
        return True
            
    def handle_message(self, msg):
        '''Checks for required fields and routes according to purpose and sender_id'''
        rsp = ''
        if not msg:
            rsp = False
        if not self.missing_rqrd_fields(msg):
           print( "Error. Message must contain required fields: ")
           # TODO: decide if should exit or just return
        purpose = msg["purpose"]
        sender_id=msg["sender_id"]
        msg_id = msg["msg_id"]
        print(f" purpose: {purpose}  sender: {sender_id}  msg_id: {msg_id}")
        if purpose == -1:
            rsp = False
        if purpose == 0:
            obj =  {"purpose": 1, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "greet": f"Welcome  {sender_id}" }
            rsp =  json.dumps(obj)
        if purpose == 10:
            obj = {"purpose": 11, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "cfg_id": self.cfg_ids }
            rsp = json.dumps(obj)
        if purpose == 20:
            obj = {"purpose": 21, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "lut": self.luts[0] }
            rsp = json.dumps(obj)
        if purpose == 30:
            obj = {"purpose": 31, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "lut": self.luts[1] }
            rsp = json.dumps(obj)
        if purpose == 40:
            obj = {"purpose": 41, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "lut": self.luts[2] }
            rsp = json.dumps(obj)
        if purpose == 60:
            obj = {"purpose": 61, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "config0": self.cfg[0][:-1], "config1": self.cfg[1][:-1], "config2": self.cfg[2][:-1]}
            rsp = json.dumps(obj)
        if purpose == 50:
            obj = {"purpose": 51, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "status": "Ready for Business"}
            rsp = json.dumps(obj)
#         if purpose == 100:
#             #has to be re-sent to the adc_client which will do the measurement.
#             chan=msg["chan"]
#             obj = {"purpose": 100, "sender_id": "server", "msg_id": self.nextmsgid(),
#                     "chan": chan }
#             rsp = json.dumps(obj)
#             self.messages_for_adc.append(rsp)
#             print("msgs_for_adc: ",self.messages_for_adc )
        return rsp
    
    
       
        
        
        
        
