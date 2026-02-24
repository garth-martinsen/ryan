# file: adc.py to mimic the real adc...

from collections import namedtuple
import json
from message_cfg import measures, calibs , msr_samples,clb_samples

class ADC():
    def __init__(self):
        self.received_messages=[]

    def build_response(self, msg):
        self.received_messages.append(msg)
        if msg == 'sd':
            return msg
        else:
            parts = msg.split(",")
            purpose=parts[0]
            chan=int(parts[1])
            if purpose == '100':
                return self.measure(chan)
            if purpose == '200':
                return self.calibrate(chan)
            
    def measure(self, chan):
        return json.dumps(measures[chan] )
    
    def calibrate(self, chan):
        print(calibs[chan])
        return json.dumps(calibs[chan])   
    

    def measureAllThree(self):
        msg = [] 
        for r in self.responses:
           msg.append(r)
        return json.dumps(msg)
 
