# file:  gui_data_controller.py  #data handler in the gui_client.py

import json
#from copy import deepcopy
from collections import OrderedDict

MESSAGE_PURPOSES ={0: "HELLO", 1: "WELCOME CLIENT", 10: "rqst_cfg0", 11:"cfg0",
                   12: "rqst_cfg1", 13: "cfg1",  12:"rqst_cfg2", 13:"cfg2", 14: "cfg2", 50: "notify_ready",
                   51: "ack_ready",  100: "rqst_meas_chan", 101: "meas_chan", 150: "schedule_measure",
                   175: "get_meas_records", 176: "list<measure_records>",  200: "rqst_calib_chan_vin",
                   201: "calib_chan_vin", 250: "rqst_step_calib",  275: "get_calib_records", 276: "List<calib_records>"}
                

DISCONNECT_MESSAGE = json.dumps(
    {"purpose": -1, "sender_id": "gui_client", "desc": "DISCONNECT"}
)

CONFIGURING = 0
USER_REQUESTING = 1
modes=[CONFIGURING,USER_REQUESTING]

sender_id = "gui_client"

class GuiDataController:
    def __init__(self, cfg_ids, conn):
        self.client_name = "gui_client"
        self.mode = CONFIGURING
        self.cfg_ids = cfg_ids
        self.luts = [{}, {}, {}]
        self.configs = [ [], [], [] ]  # all fields in CONFIG table (except luts)
        self.status = 'Pending'
        self.measurements = [ [], [], [] ]  # all records from BMS table where type='m'
        self.calibrations = [ [], [], [] ]  # all records from BMS table where type='c'
        self.rqsts_to_svr=[]
        self.resps_from_svr=[]
        self.svr_msgs_cnt=0
        self.msg_start =  {"purpose": 0, "sender_id": "gui_client", "msg_id": -99}
        self.msg_id = 6000     #starting msg_id in gui_data_controller...
        self.responses_for_purpose =  OrderedDict()
        self.load_responses()
        self.conn = conn

    def load_responses(self):
        lr=self.responses_for_purpose
        lr[ 1] =  {"purpose": 10, "sender_id": "gui_client", "msg_id": self.nextmsgid()}
        lr[11]=  {"purpose": 12, "sender_id": "gui_client", "msg_id": self.nextmsgid()}
        lr[13]=  {"purpose": 14, "sender_id": "gui_client", "msg_id": self.nextmsgid()}
        lr[15] = {"purpose": 50, "sender_id": "gui_client", "msg_id": self.nextmsgid()}
#         lr[51] = {"purpose":100, "sender_id": "gui_client", "msg_id": self.nextmsgid()}
#         lr[101] =  {"purpose": 200, "sender_id": "gui_client", "msg_id": self.nextmsgid()}                 
#         lr[201] =  {"purpose": 150, "sender_id": "gui_client", "msg_id": self.nextmsgid(),"wait_secs": 5, "reps":5}
         
  
    def kill_process(self):
        ''' kills the process with the name: "Python db_server.py"  '''
        import cysignals
        import os, signal
        name ="Python db_server.py"
        try:
            # iterating through each instance of the process
            for line in os.popen("ps ax | grep " + name + " | grep -v grep"): 
                fields = line.split()
                print("Pid: ", fields[0])
                # extracting Process ID from the output
                pid = fields[0]
                # terminating process 
                os.kill(int(pid), signal.SIGKILL) 
            print("Process Successfully terminated")
        
        except:
            print("Error Encountered while running script")

        
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
        print("Called gdc.handle_message(...). will return next msg to send to server.")
        #following three values will be extracted and overwritten from msg.
        purpose=-2
        sender_id=''
        msgid=''
        if self.has_rqrd_fields(msg):
            purpose = msg["purpose"]
            sender_id=msg["sender_id"]
            msgid = msg["msg_id"]
            print ("msg: ",msg, " p: ",purpose, " s: ", sender_id, " m: ",msgid )
        if self.mode == CONFIGURING:
            obj = self.configure(msg, purpose)
        if self.mode == USER_REQUESTING:
            obj = self.user_requests()
        return obj

    def configure(self, msg, purpose):
        ''' auto fetch: cfg_ids, luts, configs,READY, then 150(schedule_measures)'''
        obj=None
        if purpose < 50:
            obj = self.responses_for_purpose[purpose]
        # harvest response data
        if purpose == 1:
            print( f"Recognized and registered with server purpose: {purpose}")
        if purpose == 11:
             self.configs[0]= msg["cfg0"]
             self.luts[0]= self.configs[0][-1]
             self.configs[0]= self.configs[0][:-1]
        if purpose == 13:
            self.configs[1]=msg["cfg1"]
            self.luts[1]= self.configs[1][-1]
            self.configs[1]= self.configs[1][:-1]
        if purpose == 15:
            self.configs[2]=msg["cfg2"]
            self.luts[2]= self.configs[2][-1]
            self.configs[2]= self.configs[2][:-1]
            self.user_requests()
        if purpose == 51:
             print("status: " ,msg["status"])
             self.mode=USER_REQUESTING
             self.status = 'READY'
        if obj:
            return json.dumps(obj)

#    TODO  8: Figure out how to deal with on demand stuff.
#    TODONE 8: Added field mode[CONFIGURING| USER_REQUESTING ]. If mode==USER_REQUESTING, then call user_requests()
#     to capture rqrd args and return a dict

    def user_requests(self):
        ''' uses input to capture user inputs, create a dict  and return it as a string'''
        purpose = int(input( "purpose: "))
        obj=None
        if purpose == 100:
            chan = int (input("chan: "))
            obj=  {"purpose": purpose, "sender_id": sender_id, "msg_id": self.nextmsgid(), "chan": chan}
        elif purpose == 200:
            chan = int (input("chan: "))
            vin = float(input("vin: "))
            obj=  {"purpose": purpose, "sender_id": sender_id, "msg_id": self.nextmsgid(), "chan": chan, "vin": vin }
        elif purpose == 150:  #schedule measurements
            wait_secs = int(input("wait_secs: "))
            reps =int(input("repetitions: "))
            obj=  {"purpose": purpose, "sender_id": sender_id, "msg_id": self.nextmsgid(), "wait_secs": wait_secs, "reps": reps }
        elif purpose == 175:       # fetch meas records
            chan = int(input("chan: "))
            obj=  {"purpose": purpose, "sender_id": sender_id, "msg_id": self.nextmsgid(), "chan": chan }
        elif purpose == 250:   #stepping calibs
            wait_secs = int(input("wait_secs: "))
            chan = int (input("chan: "))
            obj =  {"purpose": purpose, "sender_id": sender_id, "msg_id": self.nextmsgid(),
                   "wait_secs": wait_secs, "chan": chan }
        elif purpose == 275:   # fetch calib records
            chan = int (input("chan: "))
            obj =  {"purpose": purpose, "sender_id": sender_id, "msg_id": self.nextmsgid(), "chan": chan }
        print(f" user_requests() . line 178 obj: {obj}")
        return json.dumps(obj)
        
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
 
    def schedule_measurements(self, wait_secs, reps):
         '''Schedules repeating measurements on all three circuits. Results saved to db table BMS.
         Wait time is seconds between measurement action,reps is number of repetitions.'''
         print(f"Schedule Measurements every {wait_secs} for {reps} repetitions ")
         obj = {"purpose":150, "sender_id": "gui_client",  "msg_id": self.nextmsgid(),
                "wait_time": wait_secs, "reps": reps}
         msg= json.dumps(obj)
         return msg

    def stepping_calibrations(self, wait_secs, chan):
         '''One-tenth volt steps of vin on channel, chan. Saves vin and vm to db table BMS.
         User has wait_secs to set input voltage on adjustable power supply, before msg is sent.'''
         print(f"Step through vin in 1/10 volt increments on channel: {chan} ")
         obj = {"purpose": 250, "sender_id": "gui_client",  "msg_id": self.nextmsgid(),
                "wait_time": wait_secs, "reps": reps}
         msg= json.dumps(obj)
         return msg

def log(self):
        self.show_gui_data()
        print()
        print(f"gui_client requests_to_server:                 {self.rqsts_to_svr} ")
        print(f"responses_to_gui_client from_server:     {self.resps_from_svr} ")
        print(f"server msgs_received by_gui_client count:  {self.svr_msgs_cnt}")
        print(f"msg_id: {self.msg_id}")
        