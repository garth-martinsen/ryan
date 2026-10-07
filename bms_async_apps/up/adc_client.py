# file: up/adc_client.py

from up.adc_cfg import Config
from up.volts_adc import VoltsAdc
from up.amps_adc import AmpsAdc
from common.bms_config import SVR_IP, SVR_PORT, APP_ID, VERSION
from collections import OrderedDict
from machine import RTC
import asyncio
import json
import time

print(f"From bms_config, SVR_IP: {SVR_IP}, SVR_PORT: {SVR_PORT}")
# TODO 3: Create a self.dict to hold all holdover values key=msgid value= [] list will hold: code, msgid, vins, type, 
# TODO 3: self will store the holdovers when msg arrives and pull them out for the report_to_svr.'''
class AdcClient:
    def __init__(self):
        '''Creates empty AdcClient which will get config from db table, create volt_adc and amps_adc, load the handlers_dict with functions to call when msgs arrive.'''
        self.reader = None
        self.writer = None
        self.config = None
        self.msgid  = None
        self.meas_id = None
        self.amps_measurement_period = None
        self.amps_meas_reps = None
        self.volts_meas_reps = None
        self.amps_meas_done = None
        self.volts_meas_done = None
        self.volts_measurement_period = None
        self.handlers_dict = OrderedDict()
        self.volts_adc = None
        self.amps_adc = None
        self.registered_with_server = False
        self.holdover_dict = OrderedDict()
        
        print("Created Empty AdcClient. It will be populated in start() function")

    def call_function( self, code, arglist):
        print(f" code: {code}   function: {self.handlers_dict[code].__name__} arglist: {arglist}")
        return self.handlers_dict[code]( *arglist )

    async def send(self, request):
        '''request is a dict. It must be stringified, terminated by "\n" and  converted to bytes.
           RECEIVER is always the Svr'''
        msg = (json.dumps(request) + "\n").encode()
        print("Sending msg: ", msg)
        self.writer.write(msg)
        await self.writer.drain()

    def next_meas_id(self):
        self.meas_id +=1
        return self.meas_id

    def is_commissioned(self):
        print((self.is_registered, self.have_time, self.have_meas_id, self.have_config))
        if self.is_registered and self.have_time and self.have_meas_id and self.have_config:
            self.commissioned.set()
            print("adc_client Is commissioned!")
            #print(f"In adc_client.is_commissioned() ")

    async def receive_loop(self):
        while True:
            line = await self.reader.readline()
            if not line:
                print("raw line from svr: ", line)
                #continue
                raise OSError("Server closed the connection")
            
            msgin = json.loads(line.decode())
            print("msgin & type: ",type(msgin),  msgin)
            code = msgin["CODE"]
            if code in [30,32,40,42]:
                self.save_holdovers(msgin)
            arglist = msgin["ARGLIST"]
            self.call_function(code, arglist)

    async def send(self, request):
        '''request is a dict. It must be stringified, terminated by "\n" and  converted to bytes.
           RECEIVER is always the Svr'''
        msg = (json.dumps(request) + "\n").encode()
        print(f"Sending msg: {msg}")
        self.writer.write(msg)
        await self.writer.drain()


    def save_holdovers(self, msg):
        ''' Fields held in self.holdovers_dict will be injected into the report_to_svr msg.Add fields as needed...'''
        self.holdover_dict =OrderedDict({"MSGID":msg["MSGID"], "CODE": msg["CODE"],"TYPE": msg["TYPE"], "VINS": msg["VINS"]})

    # TODO 1: Need to register with server, sync_time, get_meas_id_seed, get_app_config, . Right now hanging in self.send(). Ask Chat.
    async def start(self):
       self.commissioned = asyncio.Event()
       self.is_registered = False
       self.have_time = False
       self.have_meas_id = False
       self.have_config = False

       # connect to the server..
       self.reader, self.writer = await asyncio.open_connection( SVR_IP, SVR_PORT)

       #populate self.handlers_dict... let hd be used for brevity
       hd = self.handlers_dict
       hd[1]  = self.handle_registration
       hd[3]  = self.handle_time_sync
       hd[5]  = self.handle_meas_id_seed
       hd[11] = self.handle_app_config
       hd[30] = self.measure_volts
       hd[32] = self.start_periodic_voltage_measurements
       hd[40] = self.calibrate_volts         #40 same as 30, inputs & reports differ. 
       hd[42] = self.start_periodic_calibrations #42 same as 32, inputs & reports differ.
     
       #start one and only receive loop
       asyncio.create_task(self.receive_loop())

       #Send the four commissioning requests and wait for commissioned_event..
       msg1 = await self.register_with_server()
       await self.send(msg1)
       msg2 = await self.get_svr_time_sync() 
       await self.send(msg2)
       msg3 = await self.get_meas_id_seed() 
       await self.send(msg3)
       msg4 = await self.get_app_config()
       await self.send(msg4)
       await asyncio.wait_for(self.commissioned.wait(), 10)

    async def register_with_server(self):
        return { "SENDER": "ADC", "RECEIVER": "SVR", "CODE": 0 }

    async def get_svr_time_sync(self):
        return {"SENDER": "ADC", "RECEIVER": "SVR", "CODE": 2, "ARGLIST": [] }

    async def get_meas_id_seed(self):
        return {"SENDER": "ADC", "RECEIVER": "SVR", "CODE": 4, "ARGLIST": [] }

    async def get_app_config(self):
        return  { "SENDER": "ADC", "RECEIVER": "SVR", "CODE": 10, "ARGLIST": [] }

    def handle_registration(self):
        print("Is registered with SVR ")
        self.is_registered = True
        self.is_commissioned()
        
    #TODO 2: Make sure that setting rtc.datetime on one adc will update the other adc. If not need to set both adcs.

    def handle_time_sync(self, svr_tup):
        ''' Since the rtc.datetime() function is set on the base class, both volts_adc and amps_adc wil have correct time.'''
        print("In handle_time_sync received svr_tup: ", svr_tup)
        #svr_tup = msg["SVR_TUP"]
        # must insert day_of_wk (svr_tup[6]) between date and time entries.
        esp_tup = (svr_tup[0], svr_tup[1],svr_tup[2],svr_tup[6],svr_tup[3],svr_tup[4],svr_tup[5],0)
        RTC().datetime(esp_tup)
        self.have_time = True
        self.is_commissioned()

    def handle_meas_id_seed(self, meas_id):
        print(f"in handle_meas_id meas_id is: {meas_id}")
        self.meas_id = meas_id
        self.have_meas_id = True
        self.is_commissioned()
        
    def handle_app_config(self, config):
       #Extract config info from msg. 
       print(f"in handle_app_config, config: {config}")
       self.config = Config(*config)
       #Create the two adc instances...
       self.volts_adc = VoltsAdc(self.config)
       self.amps_adc =  AmpsAdc( self.config )
       self.have_config = True
       self.is_commissioned()

    async def measure_volts(self, msg):
        ''' Returns nothing. volts_adc will put a2d and uclicks into memory for each channel, to be used when report_to_svr is called.'''
        self.holdover_dict = OrderedDict({"VINS" : msg["VINS"], "MSGID": msg["MSGID"], "CODE":msg["CODE"], "TYPE": msg["TYPE"]})
        for chan in range(3):
            self.volts_adc.measure(chan)
            self.volts_adc.timestamps[chan]= time.time()
        return await self.report_to_svr()

    async def start_periodic_voltage_measurements(self, msg):
        ''' Returns nothing.This is an asynchronous task. Each channel is measured before waiting...
            Arg msg is a dict. Measurements will repeat until reps are completed or it is stopped by User thru GUI.'''
        period = msg["PERIOD"]
        reps = msg["REPS"]
        msgid= msg["MSGID"]
        self.holdover_dict = OrderedDict({"VINS" : msg["VINS"], "MSGID": msgid, "CODE":msg["CODE"], "TYPE": msg["TYPE"]})
        self.volts_measurement_period= period
        self.volts_meas_reps=reps
        print(f"from start_periodic_voltage_measurements msg: {msg} ")
        self.volts_reps_done=0
        for rep in range(reps):
            for chan in range(3):
                self.volts_adc.measure(chan)
            self.report_to_svr()
            self.volts_reps_done += 1
            print(f"Completed {self.volts_reps_done} repetitions of period voltage measurements")
            if rep < reps - 1:
                await asyncio.sleep(period)
        print(f"All of volts_meas_reps: {self.volts_meas_reps} are done.")
        
    async def calibrate_volts(self, msg):
        '''Returns nothing.It will cause a voltage_measurement_report to the svr eventually...'''
        pass
                
    async def start_periodic_calibrations(self, msg):
        '''Returns nothing.It will cause many voltage_measurement_reports to the svr eventually...'''
        pass

    async def report_to_svr(self):
        '''get the form, populate my part, get volts_adc's part, get amps_adc's part . When complete send it.'''
        print(f"in adc_client.report_to_svr(), holdover_dict: {self.holdover_dict}")
        vins = self.holdover_dict["VINS"]
        report = self.voltage_report_form()
        report["MEAS_ID"]= self.next_meas_id()
        report["MSGID"]= self.holdover_dict["MSGID"]
        report["TYPE"]=self.holdover_dict["TYPE"]
        report["CODE"]=self.holdover_dict["CODE"]+1 
        # pass the report to each of the adcs to add their portions.
        self.volts_adc.report_to_svr(report, vins)
        self.amps_adc.report_to_svr(report)
        # send the report to the server.
        print(f"in adc_client.report_to_svr() after all population: {report}")
        print("Completed report; about to send")
        await self.send(report)
        print("send() finished")
        return report 
        
    def voltage_report_form(self):
       '''This form will be used by self, volts_adc and amps_adc to fill in their values. Completed rpt will then be sent by AdcClient.'''
       return {"SENDER":"ADC", "RECEIVER":"SVR", "APP_ID":1, "VERSION":3, "CODE": 101,
                "MSGID": 123, "MEAS_ID":1, "TYPE":"m", "CHANS":[ 
                  {"CHAN":0, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #A2D : 64 values.. 
                  {"CHAN":1, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #likewise
                  {"CHAN":2, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #likewise
                  {"CHAN":3, "TIMESTAMP": 178000.0, "I_MEAN":0.550,"PERIOD_SEC":3600, "AH_USED":0.550 } #filled by amps_adc. 
                 ]}

async def main():
    client = AdcClient()
    await client.start()

    # Keep running after commissioning.
    await client.receive_task

if __name__ == "__main__":
    asyncio.run(main())
