# file: create_gui_cmds.py
import time
from collections import OrderedDict

#global vars.
counter = 0;

class CreateGuiCmds:
    def __init__(self, filename):
        self.filename = filename
        self.gui_cmds = OrderedDict()
        
        

    def show_cmds(self):
        print( f" GUI cmds stored in gui_cmds dict: ")
        for k,v in self.gui_cmds.items():
            print()
            print(k,v)
            print()
            
    def collect_cmds(self):
        global counter
        while True:
            counter +=1
            self.gui_cmds[counter] = self.get_msg()
            self.show_cmds()

    def _timestamp(self):
        ''' Returns a float eg: ... if this float is input to function human_timestamp( it will return a human readable string'''
        return time.time()
    
    def human_timestamp( tm: float):
        ''' Returns human-readable string  eg: '2026-06-20 10:59:01' '''
        return datetime.datetime.fromtimestamp(tm).strftime('%Y-%m-%d %H:%M:%S')

    def get_msg(self):
        ''' Formats msg with cmd values to the Server'''
        # print("Respond to promps. They will change depending on code (command). ")
        ts = self._timestamp()
        receiver = input("RECEIVER: " )
        sender = 'GUI'
        code = int(input("CODE: " ))
        msg =  {"RECEIVER": receiver , "SENDER" : sender, "TIMESTAMP": ts, "CODE": code}
        msg["ARGLIST"]=[]
        if code == 1:
            print(msg)
        if code == 175:
            msg["PERIOD" ]= int(input("period: "))
            msg["REPS"]  =int( input("repetitions: "))
        if code  == 100:
            msg["TYPE"] = input("type: " )
            msg["VIN"] = 0.0
        if code == 200:
            msg["VIN"] = float(input("vin: "))
            msg["CHAN"] = int(input("chan: " ))
        if code == 274:
            msg["VIN"] = float(input("vin: "))
            msg["CHAN"] = int(input("chan: " ))
        if code in [ 300,310,320, 330, 340, 350, 360, 370]:
            for k, v in funct_desc.items():
                print(k,v)
                
            msg["ARGLIST"] = json.loads(input("arglist: "))      #input returns a stringified list . needs to be a list
            
        print(f"\tGUI client sending msg: {msg}")
        return msg  
