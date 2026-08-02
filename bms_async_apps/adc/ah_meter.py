# file: /adc/ah_meter.py   purpose: accumulate amps measured vi module ammeter and when triggered, return ah_used...

import time

class AhMeter:
    '''Inits as empty. Starts with input_time, input_vtap, sets count=0, and accumulates & counts current measurements until 
       adc_client asks for ah_used, responds by multiplying average current by delta_time to return ah_used.''' 

    def __init__(self):
        self.start_time=0.0    # start_time passed in on start(),  end_time is passed in when adc_client asks for ah_used.
        self.amp_sum = 0.0     # accumulates periodic measurements until ah_used(..) is called.
        self.vtap = 0.0        # indicates voltage at which ah_used is needed.
        self.count=0           #if measure every minute, should get ~ 60 current measurements in the hour wait for next Voltage measurement.
    
    def start(self, vtap:float, start_time:float):
        self.start_time =start_time 
        self.amp_sum = 0.0
        self.count = 0
        self.vtap = vtap

    def add_amps(self, amps: float):
        self.amp_sum += amps
        self.count += 1

    def ah_used(self, end_time ):
        delta_time_hr= (end_time - self.start_time)/3600   #in hours should be ~1.0
        avg_amps = self.amp_sum / self.count
        ah_used = delta_time_hr *  avg_amps
        print(f"delta_time_hr : {delta_time_hr} avg_amps = {avg_amps}  ah_used : {ah_used}")
        return  ah_used

#===================
# tests found in tests/test_ah_meter.py

