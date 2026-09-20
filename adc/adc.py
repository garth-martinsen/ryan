#file: adc.py

import  time 
import math
import json
from collections import OrderedDict
from common.bms_config import APP_ID, VERSION
from ads1x15 import ADS1115
from machine import SoftI2C, RTC
from adc.adc_cfg import ADC_SAMPLE_RATE, _BUFFERSIZE, NAMES, Pin, Measurements, Stats, measurements
scl=Pin(5)
sda=Pin(4)
alert = Pin(17)
i2c = SoftI2C(scl, sda)
#ADC_ADDRESS = 0x48
#ADC_GAIN = 1   #for voltage channels: gain=1 FSR=4.096V...   when needed switch to gain=3 for amps channel: FSR=1.024V
ads=ADS1115(i2c)    # ADC sampler
cnt=0
class ADC:
    """ ADC class monitors 3 voltage circuits (4V, 8V, 12V , which are chans[0,1,2]). 
    To Sample a circuit: set appropriate adc_gain , monitor irq pin for alert signal. 
    At ea alert signal , the irq method stores a2d count and ticks_us until _BUFFERSIZE
    samples are stored.  This results in two arrays per channel stored in ESP memory:
    a2d and uclicks. RAM memory will hold data for all three channels.
    The ADC can receive 2 types of message: Set up Periodic ( code: 175, 275), 
    Measure on Chan (code:100 or 200).  The measurement cmd can be of two types: 
    calibrate (code=200, vin is not 0) and plain measure (code=100, vin=None).
    The msg id,vins,etc from the requesting msg are put back into the response msg, the return code =rqst.code+1.
    """
    def __init__(self, APPID, VERSION):
        self.app_id = APPID
        self.version=version
        self.names = NAMES
        self.pins = allPins
        self.measurements = measurements
        self.index_put = 0
        self.adc_sample_period = 1 / _BUFFERSIZE
        self.i2c = i2c
        self._check_i2c()
        self.adc_gain_per_chan = {0:1, 1:1, 2: 1, 3: 3}             # integers are indices in ads1x15 : 1 means: 4.096, 3 means 1.024
        self.adc_steps = 32768
        self.lsb = self.adc_fsr/self.adc_steps
        self.msgid = None   #This will be set by calling method
        self.meas_id = None   #This will be set by svr at startup in  method
        self.sda=sda
        self.scl=scl
        self.alrt=alert
        self.rtc = RTC()
        self.msg={}
        self.timestamps = []
        self.vins = [0,0,0] # set in calibrate(...) else remains Zeros
        self.current_measurement_period = 60  #seconds default value is 60 seconds but can be set by a gui msg.
        self.volt_measurement_period = 3600   #seconds == 1 hour.
        self.reporting = 0 # adc will set this variable in method report_to_server
        
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

    def next_meas_id(self):
        '''ADC is delegated the authority to create meas_id for each voltage-report_to svr. 
           ADC.meas_id is set from server via TCP at startup of ESP32.Svr just gets max meas_id from bms table and returns it to ADC.
           After that, ADC  just increments by 1 each new meas_id'''
        self.meas_id +=1
        return self.meas_id

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

    def measure(self, ch):
        """Prepares circuits[ch] to measure voltage at the sample point.
        Vin is not needed for a measurement. Its value gets added in report_to_svr(...) when needed for calibration"""
        global cnt
        # !!!always reset the counter, index_put,  before a measurement.!!!
        self.index_put = 0
        cnt = 0
        self.channel = ch
        # add handler for irq
        self.pins.alert.irq(trigger=Pin.IRQ_FALLING, handler=self._sample_auto)
        # ads.gain is an integer from ads1x15.py: 1 means FSR=4.096V 3 means FSR=1.024V See:lines 99-106 in ads1x15.py 
        ads.gain = self.adc_gain_per_chan[ch] 
        ads.conversion_start(ADC_SAMPLE_RATE, ch)
        # if channel==0 the a2d values will come from A0, if 1 then A1, if 2 then A2
        print("===========measuring=========")
        #print( f" Wait for {_BUFFERSIZE} samples on channel {ch}  FSR: , {self.adc_fsr}, LSB : {self.lsb}")
        # loops until a2d and uclicks arrays are filled
        while self.index_put < _BUFFERSIZE:
            pass
        #TODO 2: Make sure this is the correct timestamp for the bms table.
        self.timestamps[ch]= time.time()
        #print(f"Done...A2D samples will be found in self.measurements[{ch}].a2d")
        # measurements are stored in measurements arrays They will be loaded from there into the server_report...

    def build_report_to_svr(self, server_report, msgid, vins, code):
        self.reporting =1
        name = self.names[int(chan)]
        # report depends on the code: set_up, measure or calibrate
        if code in [ 100, 174] :
            server_report["TYPE"]='m'
        elif code in [ 200, 274]:
            server_report["TYPE"]='c'
        server_report["MSGID"] = msgid                  #preserve the msgid the svr stamped on gui request to adc.
        server_report["CODE"] = code+1                  #Policy: Add 1 to the requesting code. 
        server_report["MEAS_ID"] = self.next_meas_id()  # here is where the meas_id is created and set.
        for ch in range(3):
            chan= server_report["CHANS"][ch]
            chan["A2D"]= self.measurements[ch].a2d
            chan["TIMESTAMP"]=self.timestamps[ch]
            if code == 200:
                chan["VIN"] = vins[ch] 
        # Policy:  the json.dumps  and add "\n" are always done by the adc_asyncio_client.py before a send.
        # So this function returns a dict when called by adc_asyncio_client.
     

#=======delete below this line ==== 

