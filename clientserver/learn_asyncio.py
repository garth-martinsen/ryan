# file: learn_asyncio.py

import asyncio
from asyncio_cfg import measurement, steps_per_channel
import json
import time

class myscheduler:
    '''This scheduler is used by the FLET GUI to send msgs to the db_server, which ,in turn, forwards
       the msgs to the adc_client to make measurments and calibrations. To set up repeating measurements
       , the GUI must set wait_period and reps first. For a channel calibration, the Gui must also set the
       wait_period, the time between the different steps in vin (eg: 3 seconds) to allow for the
       power supply voltage to be set and accurately measured (vin).  '''
    def __init__(self):
        self.wait_period=0     # user sets it to number of secs to wait before repeating.
        self.reps = -1             # user sets it to a finite number, may be a very large number.
        self.responses = [{},{},{}]
        self.requests=[{},{},{}]
     #TODO: Implement Steppiing Calibration
    #TODO: Fold this functionality into the scheduler_client, which will send/receive msgs from db_server.

    def timestamp(self):
        '''Returns local time as string, eg: YYYY-mm-DD HH:MM:SS'''
        dt = time.localtime()
        return f'{dt[0]}-{dt[1]}-{dt[2]} {dt[3]}:{dt[4]}:{dt[5]}'

    def set_wait_period(self, secs):
        '''process will repeat after secs. If step_calibrating, time before next vin...''
        self.wait_period =secs
       
    def set_reps(self, num):
        '''how many repetions of measurement sequence. If step_calibrating, not used...'''
        self.reps=num
         
    async def request_measure(self, chan):
        '''single-shot measurement on a channel. it is complete when self.responses boolean is set'''
        self.responses[chan]=False
        obj = {"purpose" : "100", "chan" : chan}
        msg= json.dumps(obj)
        #server.send(msg)
        print(f"send server msg: {msg} ")
        self.requests[chan]=msg
        while not self.responses[chan]:
            #simulate wait for server response...
            await asyncio.sleep(3)  
        #simulate response msg from server
            self.responses[chan]=measurement[chan]
        print(f"measurement from adc: {measurement[chan]} ")
        return
            
    async def wait_for_next_set(self):
        ''' wait_period is set by user in self.set_wait_period '''
        await asyncio.sleep(self.wait_period)
        
        
    async def request_calibrate(self, chan, vin):
        '''single-shot calibration of a channel, with a vin'''
        obj = {"purpose" : "200", "chan" : chan, "vin": vin}
        msg= json.dumps(obj)
        print(f"requesting calibration msg: {msg}")
        # TODO: send this msg on a socket to the db_server.
        #TODO: Fix list assignment index out of range. The number of requests will be the number of steps
        self.requests.append(msg)
        while not self.responses:
            await asyncio.sleep(3)
         #simulate response msg from server, cheat and use the measurement data.
         # Calibration: The real data will have vin and error. Error should be driven toward zero.
        self.responses.append(measurement[chan])
        print(f"calibrations from adc: {measurement[chan]} ")
        return

            
    async def request_periodic_measure(self):
        '''Repeating sequence of tasks: m(0), m(1), m(2), wait. where wait is in seconds and set by user.
        Measure all three channels in order, then sleep for waitTime , then repeat for self.reps.
        A measurement is complete when the server responds with the result.'''
#         self.requests.clear()
#         self.responses.clear()
        for n in range(self.reps):
            print(f"Running set {n+1} ")
            await self.request_measure(0)
            await self.request_measure(1)
            await self.request_measure(2)
            print(f" now: ===== {self.timestamp()}========")
            await self.wait_for_next_set()
        print(f" All Done with {self.reps} sets. Waiting {self.wait_period} seconds between sets!")
        
    async def request_stepping_calibration(self, chan):
        ''' Uses async to step thru all of the vin voltages in a channel. User must set wait_period
        as the number of seconds it takes him to adjust his power supply for the next vin. eg: 3 seconds'''
        steps = steps_per_channel[chan]
        for vin in steps:
            print(vin)
            await self.request_calibrate(chan, vin)
            await self.wait_for_next_set()
        print(f" All Done calibrating channel {chan} in {steps} steps. \
                Set wait_period higher if you need more time to set power supply. It is now at:  {self.wait_period} ")   
