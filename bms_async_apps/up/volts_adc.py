#file: up/volts_adc.py

from up.adc import Adc
from machine import Pin
import time
from array import array

class VoltsAdc(Adc):
    def __init__(self, config):
        '''Instantiate with config values.'''
        super().__init__(config)
        self.lsb = config.ADC_VOLT_FSR/config.ADC_STEPS 
        self.measurements = self.measurements[0:3]
        self.timestamps=[[],[],[]]

    def report_to_svr(self, report, vins):
        chans = report["CHANS"]
        for ch in range(3):
            self.populate_report_record(chans[ch],ch, vins[ch])
        print(f"In volts_adc.report_to_svr, report :  {report} ")
 

    def populate_report_record(self, record, ch, vin):
       ''' Fill record for ch with values'''
       record["CHAN"]=ch
       record["TIMESTAMP"] =self.timestamps[ch]
       record["VIN"] = vin
       record["SAMP_SZ"] = 64
       #, convert a2d from array to list 
       record["A2D"] = [x for x in self.measurements[ch].a2d] 
       return record

#=======comment out or delete below this line=====
'''
{"SENDER":"ADC", "RECEIVER":"SVR", "APP_ID":1, "VERSION":3, "CODE": 101,
                 "MSGID": 123, "MEAS_ID":1, "TYPE":"m", "CHANS":[
                   {"CHAN":0, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #A2D : 64 values..
                   {"CHAN":1, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #likewise
                   {"CHAN":2, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #likewise
                   {"CHAN":3, "TIMESTAMP": 178000.0, "I_MEAN":0.550,"PERIOD_SEC":3600, "AH_USED":0.550 } #filled by amps_adc.
                  ]}

'''
