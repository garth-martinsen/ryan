#file: adc.py
# Plan: strip out Gates, LUTS, STATS, format msg to send to dbs: [SENDER,RECEIVER,MSGID,CODE, TIMESTAMP, CHAN, TYPE, VIN, [A2D]] 
# file: copy simple_adc.py  class  as adc.py to gather a2d samples for a circuit, process them and prepare report for server. SIMPLIFY!!
# Goal1:    adc_client.py TBD:  receive and interpret msg from SVR ; call ADC method for 100,174, 200 , 274
#Goal2:  Return msg: msg from ADC eg:  {"frm": "adc", "to": "dbs", "id": 1001, "code": 101, "timestamp": "2026-4-29_18:31:20", "chan": 0, "type": "m", "vin": null, "samples": [16999, 17003, 17001, 17000, 17003, 17000, 17002, 16999, 16998, 16999, 17001, 17002, 16999, 17002, 17000, 17003, 16998, 17003, 16997, 17001, 17000, 17003, 17000, 17002, 17001, 16999, 17001, 16998, 16999, 16998, 16999, 17003, 16998, 16999, 17002, 17001, 17000, 16999, 16997, 17003, 16997, 16997, 17001, 17000, 16998, 17001, 16998, 16997, 17002, 16998, 16997, 16998, 16999, 17003, 17003, 17000, 16997, 16998, 17003, 17002, 16997, 16998, 17003, 16999]}
# Goal3: Add new code to synchronize time from SVR.

#TODO 1 : After Ryan gets network communication working, build the adc_client.py  to meet Goal2. In process...


import asyncio
from collections import OrderedDict, namedtuple
#from time import ticks_us, ticks_diff, ticks_ms, localtime, time
from common import bms_config
import math
import json
from ads1x15 import ADS1115
from machine import SoftI2C, lightsleep, RTC
from adc_cfg import (
    ADC_SAMPLE_RATE,
    _BUFFERSIZE,
    NAMES,
    ADC_ADDRESS,
    ADC_GAIN,
    Pin,
Measurements,
    Stats,
    measurements,
    allPins,
)

#i2c and ads
i2c = SoftI2C(Pin(5), Pin(4))
ads=ADS1115(i2c, ADC_ADDRESS, ADC_GAIN)    # ADC sampler
ADC_MSG = namedtuple("ADC_MSG", ("SENDER","RECEIVER", "CODE", "MSGID", "TIMESTAMP", "TYPE", "VERSION", "CHAN", "VIN", "SAMP_SZ", "A2D"))
cnt=0
try:
    class ADC:
        '''This module monitors 3 circuits (4V, 8V, 12V , which are chans[0,1,2]). To Sample a circuit, set appropriate adc_gain ,
    monitor irq pin for alert signal. At ea alert signal , the irq method stores a2d count and ticks_us until _BUFFERSIZE
    samples are stored.  This results in two arrays per channel stored in ESP flash memory:  a2d and uclicks. Flash memory will
    hold data for all three channels.
    The ADC can receive 2 types of message: Set up Periodic ( code: 175), Measure on Chan (code:100 or 200).
    The measurement cmd can be of two types: calibrate (code=200, vin is not 0) and plain measure (code=100, vin=0).
    The msg id from the requesting msg is put back into the response msg, the return code =rqst.code+1.
    '''

        def __init__(self, bms_config.VERSION):
            self.version=version
            self.names = NAMES
            self.pins = allPins
            self.measurements = measurements
            self.index_put = 0
            self.adc_sample_period = 1 / _BUFFERSIZE
            self.i2c=i2c
            self._check_i2c()
            self.vin = 0  # set in calibrate(...) else remains Zero
            self.adc_gain = 1
            self.adc_fsr = 4.096
            self.adc_steps = 32768
            self.lsb = self.adc_fsr/self.adc_steps
            self.msgid = None   #This will be set by calling method
            self.sda=self.pins[0]
            self.scl=self.pins[1]
            self.alrt=self.pins[2]
            self.rtc = RTC()
            self.msg={}
            #following two fields will be passed in when a msg initiated by the gui arrives from the db server. Measurements will start immediately thereafter.
#             self.measurement_period =None
#             self.measurement_reps = None
#             self.remaining= 0
            
        def set_rtc(self, ts: ()):
            '''The server has formatted the tuple for micropython, so just need to set datetime with json.loads...'''
            print(f"Svr time_sync: {ts}")
            print(f" Before setting rtc : datetime: {self.rtc.datetime()}")
            self.rtc.datetime(json.loads(ts))   
            print(f"After setting rtc.datetime: {self.rtc.datetime()} ")
            response = {"CODE": 304, "ARGLIST":[], "SENDER":"ADC", "RECEIVER": "SVR","TIME_SYNC":self.rtc.datetime() }
            return response
        
        def _check_i2c(self):
            """if ADS1115 ADDR pin is grounded, should return [72]"""
            if i2c.scan()[0]  == 72:
                print("i2c is working...")
            else:
                print("I2c is not working. Troubleshoot connections")

        def __str__(self):
            """Shows all of the self attributes..."""
            return f"adc attributes:  {self.__dict__.keys()}"

        def _timestamp(self):
            """Returns local time as string, eg: YYYY-mm-DD HH:MM:SS"""
            dt = localtime()
            return f"{dt[0]}-{dt[1]}-{dt[2]}  {dt[3]}:{dt[4]}:{dt[5]}"  # exclude day-of-week and julian date.

        async def measure(self, msgid, ch, vin, purpose):
            """Prepares circuits[ch] to measure voltage at the sample point.
            Vin = 0 for measurement and Vin= value for calibration"""
            global cnt
            # !!!always reset the counter, index_put,  before a measurement.!!!
            self.index_put = 0
            cnt = 0
            self.channel = ch
            self.msgid = msgid
            #print(f"Responding to msgid: {msgid} for code: {purpose} on chan: {ch}, with Vin : {vin}")
            # add handler for irq
            self.pins.alert.irq(trigger=Pin.IRQ_FALLING, handler=self._sample_auto)
            ads.conversion_start(ADC_SAMPLE_RATE, ch)
            # if channel==0 the a2d values will come from A0, if 1 then A1, if 2 then A2
            print("===========measuring=========")
            #print( f" Wait for {_BUFFERSIZE} samples on channel {ch}  FSR: , {self.adc_fsr}, LSB : {self.lsb}")
            # loops until a2d and uclicks arrays are filled
            while self.index_put < _BUFFERSIZE:
                pass
            #print(f"Done...A2D samples will be found in self.measurements[{ch}].a2d")
            #print("a2d cnt: ", cnt)
            return self._process_and_report(self.msgid, ch, vin, purpose)

        # IRQ method triggered by ADC ALRT pin when ADS is ready for sample to be read.
        def _sample_auto(self, x, samp=ads.alert_read):
            """Sets storage arrays depending on the active channel. """
            global cnt
            a2d = self.measurements[self.channel].a2d
            uclicks = self.measurements[self.channel].uclicks
           #print("IRQ was called")
            if self.index_put < _BUFFERSIZE:
                cnt +=1
                a2d[self.index_put] =  samp()
                uclicks[self.index_put] = ticks_us()
                self.index_put += 1

        def _process_and_report(self, msgid, chan, vin, purpose):
            '''     Returns ADC_MSG namedtuple with fields and samples. The adc_client will send the payload to storage: [file or server].'''
            # EXAMPLE"ADC_MSG: {"SENDER" : "ADC","RECEIVER" : "SVR", "CODE":101, "MSGID": 5010, "TIMESTAMP":835610636 , "TYPE":"m", "CHAN": 0, "VIN":0, "SAMP_SZ":64, "A2D":[16999, 17003, 17001, 17000, 17003, 17000, 17002, 16999, 16998, 16999, 17001, 17002, 16999, 17002, 17000, 17003, 16998, 17003, 16997, 17001, 17000, 17003, 17000, 17002, 17001, 16999, 17001, 16998, 16999, 16998, 16999, 17003, 16998, 16999, 17002, 17001, 17000, 16999, 16997, 17003, 16997, 16997, 17001, 17000, 16998, 17001, 16998, 16997, 17002, 16998, 16997, 16998, 16999, 17003, 17003, 17000, 16997, 16998, 17003, 17002, 16997, 16998, 17003, 16999]}
            print(f"in _process_and_report  purpose: {purpose} channel: {chan}")
            name = self.names[int(chan)]
            # report depends on the purpose: set_up, measure or calibrate
            code=purpose+1
            data = []
            for d in self.measurements[chan].a2d:
                data.append(d)
            if purpose == 100:
                theType='m'
            elif purpose == 200:
                theType='c'
                #TODO 4: Fix msg so that it is a dict...
            # ADC_MSG: ("frm","to", "code", "msgid", "timestamp", "type", "chan", "vin", "samples")
            adc_msg ={"SENDER":'ADC', "RECEIVER":'SVR', "CODE" : code , "MSGID": msgid, "TIMESTAMP": self._timestamp(),"TYPE": theType, "VERSION": self.version, "CHAN":chan, "VIN":vin, "SAMP_SZ":64,"A2D":data}
            print(f" ADC msg for SVR: msg type:{type(adc_msg)}  adc_msg: {adc_msg}")
            # Policy:  the json.dumps  and add "\n" are always done by the adc_asyncio_client.py. So this function returns a dict
            return adc_msg
         
 
except Exception  as e:
    print("Error:",e)
    print("file: " , e.__traceback__.tb_frame.f_code.co_filename)
    print("line no: " , e.__traceback__.tb_lineno)

#uncomment the 4 lines below to run adc.py in isolation    
    
async def main():
      adc=ADC(3)  
       
asyncio.run(main())    
    
            
