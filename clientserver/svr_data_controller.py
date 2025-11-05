#file svr_data_controller.py copied from DIST/learn/svr_data_controller_0922.py on 9/27/2025
# import time
import ast
import json
from data_controller_config import Lut_Limits, circuits, MESSAGE_PURPOSES
from database_interface import DatabaseInterface
from collections import OrderedDict
from scheduler import Scheduler 
import asyncio

FORMAT = "utf-8"
C42_steps = [x/10 for x in range(30,46)]
C84_steps = [x/10 for x in range(60, 91)]
C126_steps= [x/10 for x in range(90,136)]

#TODO 1: Find out why adc_socket is closed when this handles msgs from gui_client. Fix it so both sockets are available.
#TODONE 1 FIX: removed last line in db_server.py. handle_client:;   conn.close(). Now both sockets remain open  in dict, sockets.

class SvrDataController:
    def __init__(self, cfg_ids, sockets):
        self.cfg_ids = cfg_ids
        self.cfg = []  # cfg will hold 3 channels of dict [0,1,2]
        self.luts = [ {}, {}, {} ]  # luts will hold 3 Dictionaries: lut42, lut84 and lut126
        self.lut_limits = {}  # dict {channel: lut_limits} channels are: 0,1,2
        self.dbi = DatabaseInterface(cfg_ids)
        self.lsb0 = 6.144 / pow(2, 15)  # ~ 187.5 µvolts
        self.lsb1 = 4.095 / pow(2, 15)  # ~ 125 µvolts
        self.steps_per_channel = {0: C42_steps, 1:C84_steps, 2: C126_steps}
        self.start_msg = '{"purpose": 0, "sender_id": "server", "msg_id": self.msg_id}'
        self.msg_id = 5000
        self.load_config(self.cfg_ids)
        self.messages_for_adc = []
        self.messages_for_gui=[]
        self.scheduler=Scheduler(sockets, self)
        
    def load_config(self, ids):
        """Loads db records with ids. Converts Luts to {float:float } and sets limits to iteration.
        This method loads Calibrate View."""
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
    
    def has_rqrd_fields(self,msg):
        '''All msgs must have three foelds: purpose, sender_id, msg_id. Returns True or False.'''
        p=s=m=True
        print(f" checking required fields in msg: {msg}")
        if "purpose" not in msg:
            p=False
            print("missing required field: purpose")
        if "sender_id" not in msg:
            s=False
            print("missing required field:sender_id")
        if "msg_id" not in msg:
            m=False
            print("missing required field: msg_id")
        return p and s and m
    
    async def save_measurement(self, msg):
        """Purpose: save measurement on a channel to the db.
        The db_interface will use msg values for the insert statement.
        The cfg_id will indicate the channel"""
        msg.pop("chan")
        self.dbi.save_measurement(msg)

    async def save_calibration(self, msg):
        """Purpose: call databaseInterface to save info in table: BMS"""
        self.dbi.save_calibration(msg)

    def save_forwards(self, msg, conn, sockets, purpose, sender_id):
        '''Depending on sender_id and purpose, save to messages for_ for later sending when thread is right'''
        adc_socket=sockets["adc_client"]
        gui_socket=sockets["gui_client"]
        print("handle_forwards() was called")
        print(f" conn: {conn}  adc_socket: {adc_socket}  gui_socket : {gui_socket}")
        if purpose ==100 and sender_id == 'gui_client' and conn == gui_socket:
            #has to be re-sent by the server to the adc_client which will do the measurement.
            msg["msg_id"] = self.nextmsgid()
            msg["sender_id"]="server"
            rsp = json.dumps(msg)
            self.messages_for_adc.append(rsp)
            print("messages_for_adc: ", self.messages_for_adc)
        if purpose == 200 and sender_id == 'gui_client' :
            #has to be re-sent by the server to the adc_client which will do the calibration and return a 201.
            msg["msg_id"] = self.nextmsgid()
            msg["sender_id"]="server"
            rsp =  json.dumps(msg)
            self.messages_for_adc.append(rsp)
        if purpose ==101 and sender_id == 'adc_client' :
            #Save to db then re-send by the server to the gui_client which will present data .
            print(f" saving msg to BMS table: {msg}")
            self.save_measurement(msg)
            msg["sender_id"] = "server"
            msg["msg_id"]=self.nextmsgid()
            rsp = json.dumps(msg)
            self.messages_for_gui.append(rsp)
           # gui_socket.send(json.dumps(msg).encode(FORMAT))
       
        if purpose ==201 and sender_id == 'adc_client' :
            #Save to db then re-send by the server to the gui_client which will present the data .
            self.save_calibration(msg)
            msg["sender_id"] = "server"
            msg["msg_id"]= self.nextmsgid()
            rsp = json.dumps(msg)
            self.messages_for_gui.append(rsp)
            return rsp
        if purpose ==276 and sender_id == 'server' :
            #has to be sent by the server to the gui_client which will present the data .
            msg["sender_id"] = "server"
            msg["msg_id"]= self.nextmsgid()
            rsp = json.dumps(msg)
            self.messages_for_gui.append(rsp)
            return rsp
        #TODONE 3: Fix 300 and 400 to be dealt with as db returns to gui_client. no forwarding...
    
        
    def send_forwards(self, sockets):
        # this method pop any msg  for a socket and send it.
        adc_socket=sockets.get("adc_client", None)
        gui_socket=sockets.get("gui_client",None)
        rsp = None
        if adc_socket and self.messages_for_adc:
            print("handle_forward messages_to_adc: ", self.messages_for_adc)
            rsp = self.messages_for_adc.pop()
            adc_socket.send(rsp.encode(FORMAT))
        if gui_socket and self.messages_for_gui:
            print(" handle_forward messages_to_gui: ", self.messages_for_gui)
            rsp = self.messages_for_gui.pop()
            gui_socket.send(rsp.encode(FORMAT))
        return rsp        
        
    def handle_message(self, msg, conn, sockets):
        '''Checks for required fields and routes according to purpose and sender_id'''
        rsp = ''
        if not msg:
            rsp = False
        print(f" called sdc.handle_message(...) type(msg): {type(msg)}, msg: {msg}")
        if not self.has_rqrd_fields(msg):
           print( "Error. Message must contain required fields: ")
        purpose = int(msg["purpose"])
        sender_id=msg["sender_id"]
        msg_id = int(msg["msg_id"])
        print(f" purpose: {purpose}  sender: {sender_id}  msg_id: {msg_id}")
        adc_socket=sockets.get("adc_client", None)
        gui_socket=sockets.get("gui_client",None)

        if purpose == -1:
            rsp = False    #disconnect
        if purpose in [100,101, 200,201 ]:
            return self.save_forwards( msg, conn, sockets, purpose, sender_id)
        if purpose == 0:
            obj =  {"purpose": 1, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "greet": f"Welcome  {sender_id}" }
            sockets[sender_id]=conn
            print(f" at assignment - sockets: {sockets} ")
            rsp =  json.dumps(obj)
        if purpose == 10:
            obj = {"purpose": 11, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "cfg_id": self.cfg_ids }
            rsp = json.dumps(obj)
        if purpose == 20:
            obj = {"purpose": 21, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "lut": self.luts[0] }
            rsp = json.dumps(obj)
            #           conn.send(rsp.encode(FORMAT))

        if purpose == 30:
            obj = {"purpose": 31, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "lut": self.luts[1] }
            rsp = json.dumps(obj)
            #            conn.send(rsp.encode(FORMAT))
        if purpose == 40:
            obj = {"purpose": 41, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "lut": self.luts[2] }
            rsp = json.dumps(obj)
            #            conn.send(rsp.encode(FORMAT))
        if purpose == 60:
            obj = {"purpose": 61, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "config0": self.cfg[0][:-1], "config1": self.cfg[1][:-1], "config2": self.cfg[2][:-1]}
            rsp = json.dumps(obj)
            #            conn.send(rsp.encode(FORMAT))
        if purpose == 50:
            obj = {"purpose": 51, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "status": "Ready for Business"}
            rsp = json.dumps(obj)
        if purpose ==150 and sender_id == 'gui_client' and conn == gui_socket:
             #schedule_measurements has to be multi-sends of 100 by the server to the adc_client which will do each triple measurement.
             wait_secs = int(msg["wait_secs"])
             reps = int(msg["reps"])
             self.scheduler.set_wait_period(wait_secs)
             self.scheduler.set_reps(reps)
             asyncio.run(self.scheduler.schedule_measurements())
             # tell gui_client that measurements are scheduled and running...
             rsp=json.dumps({"purpose": 151, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "status": "Measurements  are scheduled and running..."})
             #all msgs to adc will be 100s and  responses will be 101s which are saved and forwarded  by server to gui_client.
        if purpose == 250 and sender_id == 'gui_client' and conn == gui_socket:
            # do calibrate in 1/10 v steps for vin, on channel, chan. 
             wait_secs = int(msg["wait_secs"])
             chan = int(msg["chan"])
             self.scheduler.set_wait_period(wait_secs)
             #self.scheduler.set_reps(reps)
             asyncio.run(self.scheduler.request_stepping_calibration(chan))
             #tell gui_client that calibrations are running.
             rsp=json.dumps({"purpose": 251, "sender_id": "server", "msg_id": self.nextmsgid(),
                     "status": "Calibrations are running..."})
             # a 201 will arrive at the server every "wait_secs"and will be saved in db and forwarded to to gui_client
        if purpose ==175 and sender_id == 'gui_client' and conn == gui_socket:
            # pull measurement_records  from db table BMS and return to sender.
            chan = int(msg["chan"])
            records = self.dbi.list_measurements(chan)
            obj = {"purpose": 176, "sender_id": "server", "msg_id": self.nextmsgid(), "chan": chan, "records" :records}
            rsp= json.dumps(obj)
        if purpose ==275 and sender_id == 'gui_client' and conn == gui_socket:
            # pull calibration_records  from db table BMS and return to sender.
            chan = int(msg["chan"])
            records = self.dbi.list_calibrations(chan)
            obj = {"purpose": 276, "sender_id": "server", "msg_id": self.nextmsgid(), "chan": chan, "records" :records}
            rsp= json.dumps(obj)

 
        conn.send(rsp.encode(FORMAT))
        return rsp
    
       
        
        
        
        
