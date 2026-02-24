# file: client_data_store.py
from collections import namedtuple
import json

Message = namedtuple("Message", ("timestamp", "purpose", "FSR", "LSB", "chan", "mean", "SD", "samples"))

class DataStore:
    def __init__(self):
        self.measurements = []
        self.calibrations=[]
        self.configuration=[[],[],[]]
        
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

    def show_data_store(self):
        print()
        print("Configuration: ")
        print(self.configuration)
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
                
#         timestamp = jmsg[0]
#         purpose=jmsg[1]
#         FSR=jmsg[2]
#         LSB=jmsg[3]
#         chan=jmsg[4]
#         mean= jmsg[5]
#         sd=jmsg[6]
#         samples=jmsg[7]
#         print(f"time:{timestamp} purpose: {purpose}  FSR: {FSR} LSB: {LSB} chan: {chan} mean: {mean} sd: {sd} samples: {samples} ")
     
        
        