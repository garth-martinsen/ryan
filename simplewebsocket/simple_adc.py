#file: simple_adc.py
# Plan: strip out Gates, LUTS, STATS, format msg to send to dbs: [frm,to,id,code, timestamp, chan, type, vin, samples.] 
# file: simple_adc.py  class to gather a2d samples for a circuit, process them and prepare report for server.
# Goal1:     #Goal: adc_client.py TBD: receive and interpret msg eg:  {"frm": "gui", "to": "adc", "id": 5001, "code": 100, "timestamp": "2026-4-29_18:31:20", "chan": 0, "vin": 0}
#Goal2:  Return msg: msg from ADC eg:  {"frm": "adc", "to": "dbs", "id": 1001, "code": 101, "timestamp": "2026-4-29_18:31:20", "chan": 0, "type": "m", "vin": null, "samples": [16999, 17003, 17001, 17000, 17003, 17000, 17002, 16999, 16998, 16999, 17001, 17002, 16999, 17002, 17000, 17003, 16998, 17003, 16997, 17001, 17000, 17003, 17000, 17002, 17001, 16999, 17001, 16998, 16999, 16998, 16999, 17003, 16998, 16999, 17002, 17001, 17000, 16999, 16997, 17003, 16997, 16997, 17001, 17000, 16998, 17001, 16998, 16997, 17002, 16998, 16997, 16998, 16999, 17003, 17003, 17000, 16997, 16998, 17003, 17002, 16997, 16998, 17003, 16999]}

#TODO 1 : After Ryan gets network communication working, build the adc_client.py  to meet Goal2. In process...


import asyncio
from collections import OrderedDict, namedtuple
from time import ticks_us, ticks_diff, ticks_ms, localtime, time
import math
import json
from ads1x15 import ADS1115
from machine import SoftI2C, lightsleep
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
    file_path
)

#i2c and ads
i2c = SoftI2C(Pin(5), Pin(4))
ads=ADS1115(i2c, ADC_ADDRESS, ADC_GAIN)    # ADC sampler
ADC_MSG = namedtuple("ADC_MSG", ("frm","to", "code", "msgid", "timestamp", "type", "chan", "vin", "samples"))
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

    
    def __init__(self, store_in):
        self.store_in=store_in          #one of [file, db]
        self.file_path =  file_path
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
        self.remaining= 0


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

    async def measure(self, rqst_id, ch, vin, purpose):
        """Prepares circuits[ch] to measure voltage at the sample point.
        Vin = 0 for measurement and Vin= value for calibration"""
        global cnt
        # !!!always reset the counter, index_put,  before a measurement.!!!
        self.index_put = 0
        cnt = 0
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
        '''     Returns ADC_MSG namedtuple with fields and samples. The adc_client will send the payload to storage: [file or server].'''
# Example Response msg from ADC measuring chan 0 to DBS for storage:  {"frm": "adc", "to": "dbs", "id": 5001, "code": 101, "timestamp": "2026-4-29_18:31:20", "chan": 0, "type": "m", "vin": 0, "samples": [16999, 17003, 17001, 17000, 17003, 17000, 17002, 16999, 16998, 16999, 17001, 17002, 16999, 17002, 17000, 17003, 16998, 17003, 16997, 17001, 17000, 17003, 17000, 17002, 17001, 16999, 17001, 16998, 16999, 16998, 16999, 17003, 16998, 16999, 17002, 17001, 17000, 16999, 16997, 17003, 16997, 16997, 17001, 17000, 16998, 17001, 16998, 16997, 17002, 16998, 16997, 16998, 16999, 17003, 17003, 17000, 16997, 16998, 17003, 17002, 16997, 16998, 17003, 16999]}
        print(f"in _process_and_report  purpose: {purpose} channel: {chan}")
        name = self.names[int(chan)]
        # report depends on the purpose: set_up, measure or calibrate
        code=purpose+1
        msgid=rqst_id
        data = []
        for d in self.measurements[chan].a2d:
            data.append(d)
        if purpose == 100:
            theType='m'
        elif purpose == 200:
            theType='c'
        # ADC_MSG: ("frm","to", "code", "msgid", "timestamp", "type", "chan", "vin", "samples")
        msg = ADC_MSG('adc', 'dbs', code, msgid, self._timestamp(), theType, chan, vin, data)
        #print("msg: ", msg)
        print(f" sending to datastore:  {type(msg)}  {msg} ") 
        #  return json.dumps(msg)
        return msg

    async def start_periodic_measurements(self, msgid, period, reps):
        ''' Sets up the Esp32 to make 'reps' repetitions of  measurments, spaced to occur every period seconds. '''
        print("setting period and reps, then repeating measurement and sending results periodically.")
        self.measurement_period = period
        self.measurement_reps = reps
        self.remaining = reps
        print(f"Measurements will occur every {period} seconds and repeat  {reps}  times, starting immediately")
        self.index_put = 0
        while self.remaining > 0:
            print(" Looping through all reps for each channel...")
            msg0 = await self.measure(msgid, 0,0, 100)
            await self.send_results(msg0)
            msg1 = await self.measure(msgid, 1, 0, 100)
            await self.send_results(msg1)
            msg2 = await self.measure(msgid, 2, 0, 100)
            await self.send_results(msg2)
            self.remaining -= 1
            #print(self.measurements)
            print("reps remaining: ", self.remaining)
            lightsleep(self.measurement_period)
        
        
    async def send_results(self, msg):
        if self.store_in == 'file':
            # Since this emulates the server, import of server_computes only happens in this method, which writes to file...
            from server_computes import ServerComps, lsb, vd_fracts
            sc=ServerComps()
            #TODO 4: Find out why next line cannot return all 7 params...  Done: must load module to the device each run.
            (m, vm_m, vm_sd, vb, vin, err, num) = sc.compute(msg.samples,  lsb, msg.chan, msg.vin)
            print(f"Storing adc results to: file: {self.file_path}")
            data = f"{msg.timestamp}, {msg.msgid}, {msg.code} ,{msg.type} , {msg.chan}, {m}, {vm_m}, {vm_sd}, {vb} ,{msg.vin}, {msg.vin - vb}, {num}, {msg.samples} "
            try:
                 with open(self.file_path, 'a') as file:
                     file.write('\n' + data)
                     print(f"Text appended to {self.file_path} successfully.")
            except Exception as e:
                print(f"Error: {e}")
        elif self.store_in == 'db':
            print("When network communications are complete, send to db_server...")

    async def single_measurement(self, vins):
        print("vins: ", vins)
        if sum(vins)< 1e-6:
            code = 100
        else:
            code = 200
        msg0 = await a.measure(5011, 0, vins[0], code) 
        await a.send_results(msg0)
        msg1 = await a.measure(5011, 1, vins[1], code) 
        await a.send_results(msg0)
        msg2 = await a.measure(5011, 2, vins[2], code) 
        await a.send_results(msg0)
        
async def main():
    global a
    await a.start_periodic_measurements(5010, 3600000, 168)   #wait: 1 hour =3600000 millisecs. reps: 24 hr/day * 7 days = 168 reps
    #await a.single_measurement( vins= [4.11, 8.22, 12.33] )
    #TODO 5: Get single_measurment(...) async method working so it can run while periodic is sleeping...
a=ADC('file')           #until can send to db_server, use a file on the device at 'data/adc_ storage'  
asyncio.run(main())    
        
        
#TODO 2 Design outlier rejection: DONE: let m=sum(s[2:-2])/len (s[2:-2]), then , keep =[x for x in s if abs(x-m) < 5] then use keep for stats.
#  Actual asd1115 measurements. First element is bogus on 8.4V and 12.6 V channels. Rejecting these results in errors < .05 V for ch 2  . This is fixed with outlier rejection.
# samps0 at vin= 4.2V: [24965, 24969, 24969, 24968, 24968, 24970, 24969, 24968, 24969, 24970, 24968, 24971, 24970, 24970, 24968, 24970, 24970, 24970, 24969, 24969, 24973, 24967, 24969, 24970, 24970, 24967, 24969, 24971, 24967, 24969, 24969, 24971, 24968, 24970, 24971, 24969, 24969, 24970, 24969, 24970, 24969, 24971, 24966, 24969, 24972, 24966, 24969, 24969, 24968, 24969, 24971, 24970, 24969, 24970, 24971, 24969, 24969, 24969, 24969, 24968, 24969, 24969, 24971, 24969]
#samps1 at vin=8.4V: [527, 22345, 22347, 22347, 22346, 22347, 22346, 22347, 22346, 22347, 22346, 22347, 22345, 22347, 22346, 22347, 22346, 22347, 22346, 22347, 22347, 22347, 22346, 22346, 22346, 22346, 22347, 22346, 22346, 22346, 22347, 22346, 22348, 22346, 22347, 22346, 22347, 22347, 22347, 22346, 22346, 22346, 22346, 22347, 22346, 22347, 22346, 22347, 22346, 22348, 22346, 22348, 22346, 22347, 22347, 22347, 22346, 22347, 22346, 22346, 22347, 22346, 22346, 22346]
#samps2 at vin=12.6V: [149, 25102, 25102, 25101, 25102, 25101, 25101, 25101, 25102, 25102, 25101, 25102, 25101, 25102, 25101, 25102, 25101, 25102, 25101, 25102, 25101, 25101, 25102, 25102, 25102, 25102, 25102, 25101, 25102, 25102, 25102, 25101, 25102, 25102, 25101, 25101, 25101, 25102, 25101, 25101, 25102, 25102, 25101, 25102, 25102, 25102, 25101, 25102, 25101, 25102, 25101, 25101, 25101, 25101, 25102, 25101, 25102, 25101, 25102, 25101, 25102, 25102, 25102, 25101]