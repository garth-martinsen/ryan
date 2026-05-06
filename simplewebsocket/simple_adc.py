#file: simple_adc.py
# Plan: strip out Gates, LUTS, STATS, format msg to send to dbs: [frm,to,id,code, timestamp, chan, type, vin, samples.] 
# file: simple_adc.py  class to gather a2d samples for a circuit, process them and prepare report for server.
# Goal1:     #Goal: adc_client.py TBD: receive and interpret msg eg:  {"frm": "gui", "to": "adc", "id": 5001, "code": 100, "timestamp": "2026-4-29_18:31:20", "chan": 0, "vin": 0}
#Goal2:  Return msg: msg from ADC eg:  {"frm": "adc", "to": "dbs", "id": 1001, "code": 101, "timestamp": "2026-4-29_18:31:20", "chan": 0, "type": "m", "vin": null, "samples": [16999, 17003, 17001, 17000, 17003, 17000, 17002, 16999, 16998, 16999, 17001, 17002, 16999, 17002, 17000, 17003, 16998, 17003, 16997, 17001, 17000, 17003, 17000, 17002, 17001, 16999, 17001, 16998, 16999, 16998, 16999, 17003, 16998, 16999, 17002, 17001, 17000, 16999, 16997, 17003, 16997, 16997, 17001, 17000, 16998, 17001, 16998, 16997, 17002, 16998, 16997, 16998, 16999, 17003, 17003, 17000, 16997, 16998, 17003, 17002, 16997, 16998, 17003, 16999]}

#TODO: After Ryan gets network communication working, build the adc_client.py  to meet Goal1.
from collections import OrderedDict
from time import ticks_us, ticks_diff, ticks_ms, localtime, time
import math
import json
from ads1x15 import ADS1115
from adc_cfg import (
    ADC_SAMPLE_RATE,
    _BUFFERSIZE,
    NAMES,
    ADC_ADDRESS,
    ADC_GAIN,
    SoftI2C,
    Pin,
Measurements,
    Stats,
    measurements,
    allPins,
    ads,
)
#i2c and ads
i2c = SoftI2C(Pin(5), Pin(4))
ads=ADS1115(i2c, ADC_ADDRESS, ADC_GAIN)    # ADC sampler

cnt=0

class ADC:
    '''This module monitors 3 circuits (4V, 8V, 12V , which are chans[0,1,2]). To Sample a circuit, set appropriate adc_gain ,
monitor irq pin for alert signal. At ea alert signal , the irq method stores a2d count and ticks_us until _BUFFERSIZE
samples are stored.  This results in two arrays per channel stored in ESP flash memory:  a2d and uclicks. Flash memory will
hold data for all three channels.
The ADC can receive 2 types of message: Set up Periodic ( code: 175), Measure on Chan (code:100 or 200).
The measurement cmd can be of two types: calibrate (code=200, vin is not 0) and plain measure (code=100, vin=0).
The msg id from the requesting msg is put back into the response msg, the return code =rqst.code+1.
'''

    
    def __init__(self):
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
        self.rqst_id = None   #This will be set by calling method
        self.sda=self.pins[0]
        self.scl=self.pins[1]
        self.alrt=self.pins[2]
        self.msg={}
        #following two fields will be set when a msg initiated by the gui arrives from the db server. Measurements will start immediately thereafter.
        self.measurement_period =None
        self.measurement_reps = None 


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

    def measure(self, rqst_id, ch, vin, purpose):
        """Prepares circuits[ch] to measure voltage at the sample point.
        Vin = 0 for measurement and Vin= value for calibration"""
        # !!!always reset the counter, index_put,  before a measurement.!!!
        self.index_put = 0
        self.channel = ch
        self.rqst_id = rqst_id
        print(f"Responding to msg id: {rqst_id} for code: {purpose} on chan: {ch}, with Vin : {vin}")
        # add handler for irq
        self.pins.alert.irq(trigger=Pin.IRQ_FALLING, handler=self._sample_auto)
        ads.conversion_start(ADC_SAMPLE_RATE, ch)
        # if channel==0 the a2d values will come from A0, if 1 then A1, if 2 then A2
        print("===========measuring=========")
        print( f" Wait for {_BUFFERSIZE} samples on channel {ch}  FSR: , {self.adc_fsr}, LSB : {self.lsb}")
        # loops until a2d and uclicks arrays are filled
        while self.index_put < _BUFFERSIZE:
            pass
        print(f"Done...A2D samples will be found in self.measurements[{ch}].a2d")
        print("a2d cnt: ", cnt)
        return self._process_and_report(self.rqst_id, ch, vin, purpose)

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

    def _process_and_report(self, rqst_id, chan, vin, purpose):
        '''     Returns dict with fields and samples. The adc_client will send the payload to the server.
        payload returned depends on the purpose...'''
    
#Response msg from ADC measuring chan 0 to DBS for storage:  {"frm": "adc", "to": "dbs", "id": 1001, "code": 101, "timestamp": "2026-4-29_18:31:20", "chan": 0, "type": "m", "vin": null, "samples": [16999, 17003, 17001, 17000, 17003, 17000, 17002, 16999, 16998, 16999, 17001, 17002, 16999, 17002, 17000, 17003, 16998, 17003, 16997, 17001, 17000, 17003, 17000, 17002, 17001, 16999, 17001, 16998, 16999, 16998, 16999, 17003, 16998, 16999, 17002, 17001, 17000, 16999, 16997, 17003, 16997, 16997, 17001, 17000, 16998, 17001, 16998, 16997, 17002, 16998, 16997, 16998, 16999, 17003, 17003, 17000, 16997, 16998, 17003, 17002, 16997, 16998, 17003, 16999]}

        
        print(f"in _process_and_report  purpose: {purpose} channel: {chan}")
        name = self.names[int(chan)]
        #obj = {}
        # report depends on the purpose: set_up, measure or calibrate
        if purpose == 100:
            # purpose 101 means report measurement to server.
            data = []
            for d in self.measurements[chan].a2d:
                data.append(d)
            obj = {
                "frm":'adc',
                "to" : 'dbs',
                "id" : rqst_id,                                   # same as id in rqst
                "code": 101,                                 #will be popped from dict before save to db to yield a BMS record.
                "timestamp": self._timestamp(),
                "type": "m",
                "chan": chan,
                "vin": vin,  # ignored for meas so is set to Zero
                "samples": data
            }
            print("obj: ", obj)
        elif purpose == 200:
            # 201 means report calibration to server
            obj = {
                "frm":'adc',
                "to" : 'dbs',
                "id" : self.rqst_id,                                    # same as id in rqst
                "code": 201,                                 #will be popped from dict before save to db to yield a BMS record.
                "timestamp": self._timestamp(),
                "type" : 'c',
                "chan": chan,
                "vin": self.vin,
                "samples": self.measurements[chan].a2d
            }
            print(f" reporting back to server:  {type(obj)}  {obj} ")
            self.msg=obj
          #  return json.dumps(obj)
            return obj

    def start_periodic_measurements(self, msgid, period, reps):
        ''' Sets up the Esp32 to make 'reps' repetitions of  measurments, spaced to occur every period seconds. '''
        self.measurement_period = period
        self.measurement_reps = reps
        print(f"Measurements will occur every {period} seconds and repeat  {reps}  times, starting immediately")
        # The following will be put into a separate method so the wait time can be used to sleep lightly for period seconds and reps can be counted.
        self.index_put = 0
        #self.measure(0,msgid,0,100)
#         for r in range(self.measurement_reps + 1):
#             self.measure(0,msgid,0, 100)
#             #self.measure(1,msgid, 0, 100)
#             #self.measure(2,msgid, 0, 100)
        
        print("Measurements: ")
        print(self.measurements)
#TODO Design outlier rejection, Actual asd1115 measurements. First element is bogus on 8.4V and 12.6 V channels. Rejecting these results in errors < .05 V for ch 2  
# samps0 at vin= 4.2V: [24965, 24969, 24969, 24968, 24968, 24970, 24969, 24968, 24969, 24970, 24968, 24971, 24970, 24970, 24968, 24970, 24970, 24970, 24969, 24969, 24973, 24967, 24969, 24970, 24970, 24967, 24969, 24971, 24967, 24969, 24969, 24971, 24968, 24970, 24971, 24969, 24969, 24970, 24969, 24970, 24969, 24971, 24966, 24969, 24972, 24966, 24969, 24969, 24968, 24969, 24971, 24970, 24969, 24970, 24971, 24969, 24969, 24969, 24969, 24968, 24969, 24969, 24971, 24969]
#samps1 at vin=8.4V: [527, 22345, 22347, 22347, 22346, 22347, 22346, 22347, 22346, 22347, 22346, 22347, 22345, 22347, 22346, 22347, 22346, 22347, 22346, 22347, 22347, 22347, 22346, 22346, 22346, 22346, 22347, 22346, 22346, 22346, 22347, 22346, 22348, 22346, 22347, 22346, 22347, 22347, 22347, 22346, 22346, 22346, 22346, 22347, 22346, 22347, 22346, 22347, 22346, 22348, 22346, 22348, 22346, 22347, 22347, 22347, 22346, 22347, 22346, 22346, 22347, 22346, 22346, 22346]
#samps2 at vin=12.6V: [149, 25102, 25102, 25101, 25102, 25101, 25101, 25101, 25102, 25102, 25101, 25102, 25101, 25102, 25101, 25102, 25101, 25102, 25101, 25102, 25101, 25101, 25102, 25102, 25102, 25102, 25102, 25101, 25102, 25102, 25102, 25101, 25102, 25102, 25101, 25101, 25101, 25102, 25101, 25101, 25102, 25102, 25101, 25102, 25102, 25102, 25101, 25102, 25101, 25102, 25101, 25101, 25101, 25101, 25102, 25101, 25102, 25101, 25102, 25101, 25102, 25102, 25102, 25101]