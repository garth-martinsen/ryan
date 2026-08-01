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
        self.start_time = time.time()
        self.amp_sum = 0.0
        self.count = 0
        self.vtap = vtap

    def add_amps(self, amps: float):
        self.amp_sum += amps
        self.count += 1

    def ah_used(self, end_time ):
        delta_time= end_time - self.start_time
        avg_amps = self.amp_sum / self.count
        return delta_time *  avg_amps

#===================
'''
#  test_ah_meter.py:
    def creates_empty():
    ah_meter = AhMeter()
    assert ah_meter.amp_sum == 0.0 , f"A bare metal creation of AhMeter should have amp_sum = {0.0}"
    assert ah_meter.start_time == 0.0 , f"A bare metal creation of AhMeter should have start_time  = {0.0}"
    assert ah_meter.vtap == 0.0 , f"A bare metal creation of AhMeter should have vtap = {0.0}"
    assert ah_meter.count == 0.0 , f"A bare metal creation of AhMeter should have count = {0.0}"
    
    def test_start():
    ah_meter = AhMeter()
    start_time = time.time()
    vtap = 12.6
    ah_meter.start(start_time, vtap)
    assert ah_meter.amp_sum = 0.0, f""
    assert ah_meter.count = 0, f""
    assert ah_meter.start_time = start_time, f""

    def test_ah_used():
        ah_meter = AhMeter()
        amp_sum = 13.2
        start_time = 1785601949.0
        end_time = 1785605549.0
        vtap=12.6
        ah_meter.start(12.6, start_time)
        ah_used = ah_meter.ah_used(end_time)
        assert ah_used == 13.2, f"For given parms, ah_used should equal {13.2}"

'''
