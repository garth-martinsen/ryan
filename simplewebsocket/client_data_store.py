# file: client_data_store.py
from collections import namedtuple, OrderedDict
import json

Message = namedtuple("Message", ("timestamp", "purpose", "FSR", "LSB", "chan", "mean", "SD", "samples"))

class DataStore:
    def __init__(self):
        self.measurements = []
        self.calibrations=[]
        self.configurations=[[],[],[]]
        self.luts=[[OrderedDict()],[OrderedDict()],[OrderedDict()]]
        self.lut_timestamps=[[],[],[]]
        
    def translate_message( self, msg: str):
        print("Translating message from adc_server.")
        if msg =="sd":
            self.show_data_store()    
        else:
            jmsg=json.loads(msg)
            message = Message(jmsg[0],jmsg[1], jmsg[2], jmsg[3], jmsg[4], jmsg[5], jmsg[6], jmsg[7])
            #print(f"message: {message}")
            if message.purpose == 100:
                self.measurements.append(message)
            if message.purpose == 200:
                self.calibrations.append(message)
            if message.purpose == 350:
                self.luts = self.extract_luts(message)
                self.lut_timestamps = self.extract_lut_timestamps(message)
                self.configurations = self.extract_configs(message)
                
      def extract_luts(self, message):
         #TODO 1: implement extract_luts(self, message)  see test_gui_client for hints how to implement this method
         print(f" TBD work in progress  to extract_luts() from {message}")

    def extract_lut_timestamps(self, message):
        #TODO 2: implement extract_lut_timestamps(self, message) see test_gui_client for hints how to implement this method

         print(f" TBD work in progress to extract_lut_timestamps from {message}")
    
    def extract_configs(self, message):
        #TODO 2: implement extract_configs(self, message) see test_gui_client for hints how to implement this method
         print(f" TBD work in progress to extract_configs from {message}")
    
    def show_data_store(self):
        print()

        print("Configuration: ")
        for c in self.configurations:
            print(c)
            print(("-------------------")
            print()
   
        print("Luts: ")
        for lu in self.luts:
            print(lu)
            print(("-------------------")
            print()
  
 
         print("Lut_timestamps: ")
        for lu in self.lut_timestamps:
            print(lu)
            print(("-------------------")
            print()

        print("Measurements: ")
        for m in self.measurements:
                print(m)
                print("-------------------")
        print()
 
 print("Calibrations: ")
        for c in self.calibrations:
            print(c)
            print("----------------------")
        for c in self.configurations
  
  
  
  
#         timestamp = jmsg[0]
#         purpose=jmsg[1]
#         FSR=jmsg[2]
#         LSB=jmsg[3]
#         chan=jmsg[4]
#         mean= jmsg[5]
#         sd=jmsg[6]
#         samples=jmsg[7]
#         print(f"time:{timestamp} purpose: {purpose}  FSR: {FSR} LSB: {LSB} chan: {chan} mean: {mean} sd: {sd} samples: {samples} ")
     
        
        