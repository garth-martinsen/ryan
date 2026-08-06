# file: /adc/ah_meter.py   purpose: accumulate amps measured vi module ammeter and when triggered, return ah_used...

import time
from collections import OrderedDict
from typing import List, Integer
from common.templates.adc_templates import ADC_T0_SVR_TEMPLATE

class AhMeter:
    '''Inits as commissioned with LSB, Vtap, a2d, rs,amp_gain  . 
       Starts voltage measurement interval with input_time, sets count=0, and accumulates & counts current measurements until 
       adc_client asks for ah_used, responds by multiplying average current by delta_time to return ah_used.''' 

    def __init__(self, vtap, lsb, rs, amp_gain ):
        self.start_time=0.0    # start_time passed in on start(),  end_time is passed in when adc_client asks for ah_used.
        self.amp_sum = 0.0     # accumulates periodic measurements until ah_used(..) is called.
        self.vtap = vtap       # indicates nominal voltage at which ah_used is needed. 12.6V is used for 3Cells in series. Just for show.
        self.count=0           # number of amps measurements added to amp_sum during accumulation phase.
        self.a2d = a2d         # reference to the a2d array stored by the adc on chan[3], for amps.
        self.lsb =LSB          # for FSR=1.024v and steps =2**15 ; lsb = FSR/steps, 1.024/32768 = 0.00003125 or 31.25µV
        self.rs = rs           # Measured shunt resistor value in ohms
        self.amp_gain          # Gain from INA180A1 current sense amplifier eg: 20
        self.pdict = OrderedDict() # Processing dict

    def start(self, start_time:float):
        '''Records the start time of the accumulation period, which is the cfg.ADC_VOLT_MEAS_PERIOD  '''
        self.start_time =start_time 
        self.amp_sum = 0.0
        self.count = 0

    def accumulate(self):
        '''Gets the a2d array from memory. Rejects outliers, compute mean, compute vs=self.lsb*mean, computes apparent amps, then scales it down by amp_gain  '''
        #rejects outliers by excluding bins for a2d counts more than 2 counts away from winner.
        # The winner is the a2d value whose bin holds the most counts. 
        for cnt in self.a2d:
             abin = self.pdict.get(cnt,[])
             abin.append(cnt)
             pdict[cnt]= abin
         winner = max(pdict.values)
         keep = [k for k,v in pdict.items() if abs(k-winner)< 2 ]     
         m = sum(keep)/len(keep)
         vs= self.lsb * m    #voltage across shunt resistor, rs
         apparent_amps = (vs/self.rs)                # given vs = 1 V and rs= 0.05123, then apparent_amp_s = (vs/rs)  => apparent_amps = 1.0/.05123 = 19.51981261
         cs_amps = apparent_amps / self.amp_gain     # now scale down the apparent_amps by amp_gain (20) =>  / amp_gain, so  cs_amp = 19.51981261/20 = 0.97599063 amps. 
         self.add_amps(cs_amps)

    def add_amps(self, amps: float):
        self.amp_sum += amps
        self.count += 1

    def ah_used(self):
        ''' The end_time is set in report_to_svr. ah_meter can answer everything needed in the report without any args passed in.'''
        delta_time_hr= (self.end_time - self.start_time)/3600   #in hours should be ~1.0
        avg_amps = self.amp_sum / self.count
        ah_used = delta_time_hr *  avg_amps
        print(f"delta_time_hr : {delta_time_hr} avg_amps = {avg_amps}  ah_used : {ah_used}")
        return  ah_used

    def reset(self):
        self.amp_sum = 0.0
        self.count = 0

    def report_to_svr(self, report_msg):
        '''Assuming that I can pass in report_msg and populate the amps portion of it and then later pass it to adc.report_to_svr which also updates it.  '''
        self.end_time= time.time()
        amps_chan = 3
        amps_record  = report_msg["CHANS"][amps_chan]
        amps_record["TIMESTAMP"] = self.end_time()
        amps_record["I_MEAN"]    = self.amp_sum /self.count
        amps_record["PERIOD_SEC"]= self.end_time - self.start_time
        amps_record["AH_USED"]   = self.ah_used()  
        
#===================
# tests found in tests/test_ah_meter.py
'''
amp_record:  {"TIMESTAMP": 178000.0, "I_MEAN":0.550,"PERIOD_SEC":3600, "AH_USED":0.550 }
'''

