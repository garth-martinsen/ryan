# file: svr_task_manager.py  Offloads most of the work from the bms_async_server:  routes msgs,
# returns json-worthy, correct namedtuple. The bms_async_server has requirements: 1. manage client connections,
# 2. receive json msgs,  restore python objects by json.loads(...), 2. delegate msg_processing to svr_msg_processor ,
# 3.. send json-appropriate msgs to correct async_client.

from collections import OrderedDict
from common import bms_config
from common.models.voltage_row import VoltageRow
from dataclasses import asdict
from svr.database_interface import DatabaseInterface
import json
from svr.database_interface_config import APP_CONFIG, BMS
import math

class SvrTaskManager:
    ''' Handles all msg processing and task_creation for the bms_async_svr event_loop, leaving only
    event_loop, receive, send functions to the server. Database related tasks need access to the
    database_interface (dbi), which is initialized with the app_id and version. Assumption: I can
    pass in args: event_loop, clients dict, msg, use them to create tasks on the event_loop, which
    will schedule and run the tasks.'''

    def __init__(self, app_id, version):      # removed , svr from argslist
        self.version=version
        self.app_id = app_id
        self.dbi = DatabaseInterface(app_id, version)
        self.chan_config=[[],[],[]]
        self.load_luts()
        # TODO 1: get allowance from app_config or chan_config...For now KLUGE it and just assign it.
      # allowance = how much can a measued_vb differ from the predicted_vb and still be reportable? 
        self.allowance=500e-7    
        self.measurements = {}
        self.last_vb = {0:4.044, 1: 7.89, 2: 11.95}
        self.last_vb_time = {0: 1785030326.0, 1: 1785030337.0, 2: 1785030347.0 }
        #TODO 2: load slope and intercepts from CHANNELS table via dbi
        '''│ 1.33289430358907 │ 0.024164327787965  │
           │ 2.98747763864043 │ 0.0498818752307106 │
           │ 3.99304865938431 │ 0.0641294273419395 │ '''
        self.slope=[1.33289430358907, 2.98747763864043,3.99304865938431]
        self.intercepts=[0.024164327787965,0.0498818752307106,0.0641294273419395]
        self.get_app_config()
        for chan in range(3):
            self.get_chan_config(chan)
        self.funct_dict= self.create_function_dict()

    #TODO 3: create command for gui to set adc_measurement parms...Code 10 should get all app_config attrs including measurement ones.
    #TODO 4: create methods for commented out dict items if needed...

    def create_function_dict(self):
        ''' An OrderedDict which allows self to call functions given a code and an arglist. Replaces if... elif, else.
            Note that codes: 0,2,30,32,40,42 call methods on self. The remaining codes call dbi methods.'''

        funct_dict  = OrderedDict() 
        funct_dict[4]= self.get_last_meas_id                                       # ( [ ] )
        funct_dict[10]= self.get_app_config                                   # ( [ ] )
        funct_dict[12]= self.dbi.save_config                                      # ( [cfg_id, msg:Config] )
        funct_dict[20]= self.dbi.get_chan_config                                  # ( [chan] )
        #funct_dict[22]= self.dbi.save_chan_config                                # ( [chan] )
        funct_dict[31] = self.save_report                                          # ([ rpt ])
        funct_dict[41] = self.save_report                                          # ([ rpt ])
        funct_dict[50]= self.dbi.save_to_bms                                      # ([ bms ])
        funct_dict[52]= self.dbi.list_bms                                         # ([ chan, atype])
        funct_dict[54]= self.dbi.get_bms_a2d_samples                              # ([ bms_id])
        funct_dict[60]= self.dbi.get_ah_total                                     # ([])
        #funct_dict[62]= self.dbi.save_amp_hrs                                     # ([])  TBD
        funct_dict[64]= self.dbi.get_last_amp_hrs                                 # ([])
        funct_dict[66]= self.dbi.delete_test_records                              # ([])
        funct_dict[70]= self.dbi.get_lut                                          # ( [chan] )
        funct_dict[72]= self.dbi.get_lut_item                                     # ( [chan, vin] )
        funct_dict[74]= self.dbi.update_lut_pair                                  # ([  _id,  vm,  vin] )
        funct_dict[76]= self.dbi.get_lut_timestamp                                # ([ chan ])
        funct_dict[78]= self.dbi.update_lut_timestamp                             # ([ _id,  vm,  vin] )
        funct_dict[80]= self.dbi.get_estimator_parms                              # ([chan])
        funct_dict[82]= self.dbi.update_estimator_parms                           # ([chan, slope, intercept]) 
        funct_dict[90]= self.dbi.save_GPS                                         # ([ ]) 
        funct_dict[92]= self.dbi.get_GPS                                          # ([])
        return funct_dict

    def call_function( self, code, argslist):
        print(f" code: {code}   function: {self.funct_dict[code].__name__} argslist: {argslist}")
        return self.funct_dict[code]( *argslist )

    # TODO 9: FIXED...Why is msg returned to Svr None? ANS: line xx need return self.call_function.. Consider a template starter msg..        
    def get_app_config(self):
        cfg = self.dbi.get_app_config()
        config = APP_CONFIG(*cfg)
        self.lsb=config.ADC_VOLT_FSR/config.ADC_STEPS
        #app_config = APP_CONFIG(*cfg)
        msg = self.msg_start()
        msg["CODE"]=11
        msg["ARGLIST"]=[cfg]
        print(f"config: {msg["ARGLIST"]}")
        return msg

    def msg_start(self):
        return {"SENDER": "SVR", "RECEIVER": 'ADC', "CODE": 5, "ARGLIST":[] } 

    def get_last_meas_id(self):
        meas_id = self.dbi.get_max_meas_id()
        print("meas_id: ", meas_id)
        msg = {"SENDER": "SVR", "RECEIVER": 'ADC', "CODE": 5,"MEAS_ID":meas_id,  "ARGLIST":[ meas_id] }
        return msg

    def get_chan_config(self, chan):
        cfg= self.dbi.get_chan_config(chan) 
        self.chan_config[chan] = cfg;
 #TODO 5: finish chan_config and TEST it.

    def adc_setup_periodic(self, functions_dict, argslist):
        print("Not yet implemented TBD")

    def load_luts(self):
        luts=[]
        luts.append(self.dbi.get_lut(0))
        luts.append(self.dbi.get_lut(1))
        luts.append(self.dbi.get_lut(2))
        self.luts=luts

    def get_estimator_parms(self, chan):
        self.estimator_parms = self.dbi.get_estimator_parms(chan)               

    async def send_to_client(self, name, msg, clients):
        #print(f"In send_to_client()...sending msg to {name} client. msg: {msg}")
        writer=clients.get(name)
        if writer is None:
            print(f" {name} is not connected ")
            return
        msgj=json.dumps(msg) + "\n"
        #print("msgj: ", msgj)
        writer.write(msgj.encode())
        await writer.drain()
        print(f"\tMessage sent to {name} : {msgj}")

    async def adc_calibrate(self):
        '''Sends msg from GUI_client, along with MSGID to ADC_client. msg includes: vin, type='c', chan'''
        await self.send_to_client("ADC", msg, clients)

    async def adc_measure(self):
        '''Sends msg from GUI_client, along with MSGID to ADC_client. '''
        await self.send_to_client("ADC", msg, clients)

    def predict_vb(self, chan):
        last_vb = self.last_vb[chan]
        last_vb_time = self.last_vb_time(chan)
        discharge_rate= self.discharge_rate[chan]
        delta_time = time.time() - last_vb_time
        return last_vb + delta_time * discharge_rate 

    def test_reportability(self, vb):
        ''' A chan measurememt is marked reportable iff abs(predicted_vb - measured_vb) < self.allowance'''
        vb_predicted = self.predict_vb(vb)
        return abs(vb_predicted - vb) < self.allowance

    def save_report(self, rpt):
        '''Extract a2d from rpt for each chan and process it. Delegate to DBI to persist bms. Return dict to Svr to send.'''
        #reportable= self.test_reportability(rpt)
        # save the voltage channels: 0,1,2
        chans = rpt["CHANS"]
        meas_id = rpt["MEAS_ID"]
        msgid = rpt["MSGID"] 
        version = rpt["VERSION"]
        app_id = rpt["APP_ID"]
        atype = rpt["TYPE"]
        for i in range(3):
            chan=chans[i]
            stats_result_dict = self.compute_stats(chans[i])
            error_result_dict = self.compute_error(stats_result_dict, atype)
            print(f"result type {type(error_result_dict)}  error_result_dict: {error_result_dict}")
            #("ID", "MSGID", "APP_ID","VERSION", "TIMESTAMP", "TYPE", "CHAN", "A2D_MEAN", "VM_MEAN", "VM_SD", "VB", "VIN", "ERROR", "SAMP_SZ", "DISCARD_SZ", "KEEP_SZ")
            store_to_bms_dict= {"ID" : "", "MSGID":msgid, "APP_ID": app_id, "VERSION": version, "TIMESTAMP": chan["TIMESTAMP"], 
                "MEAS_ID": meas_id, "TYPE" : atype, "CHAN" : i, "A2D_MEAN" : stats_result_dict["A2D_MEAN"],
                "VM_MEAN" : stats_result_dict["VM_MEAN"], "VM_SD" :stats_result_dict["VM_SD"], "VB" :stats_result_dict["VB"],
                "VIN" : chan["VIN"], "ERROR" :error_result_dict["ERROR"], "SAMP_SZ" : chan["SAMP_SZ"],
                "DISCARD_SZ" : stats_result_dict["DISCARD_SZ"], "KEEP_SZ": stats_result_dict["KEEP_SZ"], "A2D" : chan["A2D"]}
            print(f"store_to_bms_dict for BMS table: type: {type(store_to_bms_dict)} store_to_bms_dict:: { store_to_bms_dict} ")
            bms_id = self.dbi.save_to_bms( store_to_bms_dict )
        #AMP_HRS: ID │ APP_ID │ VERSION │ MEAS_ID │    TIMESTAMP     │ I_MEAN │ PERIOD_SEC │ AH_USED │ AH_TOTAL │
        amps_record=chans[3]
        amps_record["MEAS_ID"]=rpt["MEAS_ID"]
        print(f"amps_record: {amps_record}")
        self.dbi.save_amp_hrs(amps_record)  # chan 3 of rpt contains the above values.

    async def create_and_schedule_tasks (self, msg ):
        '''Returns dict .Based on receiver, sender and code fields, route msg to a method where it can be processed.
          The tasks will be to perform async methods. Json-worthy dict_msg is retuned to the Svr to send it to the RECEIVER  '''
        print(f"Entered method svr_task_mgr.create_and_schedule_tasks with msg of type:{type(msg)}")
        try:
            print(f"msg: {msg}")
            code = int(msg["CODE"])
            arglist = msg["ARGLIST"]
            print("reached : hw1")       
            return self.call_function(code, arglist)

        except  Exception as e:
            print("Error:", e)
            print("file: " , e.__traceback__.tb_frame.f_code.co_filename)
            print("line no: " , e.__traceback__.tb_lineno)

    def compute_error(self, channel, atype):
        '''Arg channel is one of the CHANS in rpt. Arg atype is extracted from rpt, not from a channel.
        Returns a BMS tuple with updated value for: error,
        If rpt['type'] == 'c', (calibration) the msg embedded code will be 41 or 43  and the embedded vin will be a float .
        The error is computed (error = vin-vb) . 
        If type=='m', both VIN and ERROR will be left as None.
        "DISCARD_SZ", "KEEP_SZ  embedded. The entire BMS namedtuple is defined in
        database_interface_config.py. Currently, Fields are:  BMS_FIELDS =
        ("ID", "MSGID", "VERSION", "TIMESTAMP", "TYPE", "CHAN", "A2D_MEAN", "VM_MEAN", 
        "VM_SD", "VB", "VIN", "ERROR", "SAMP_SZ", "DISCARD_SZ", "KEEP_SZ") '''
          
        if atype == 'c':
            channel["ERROR"]=channel["VIN"] - channel["VB"] 
        elif atype == 'm':
            channel["ERROR"] = channel["VIN"] = None
        return channel

    def compute_stats(self, channel):
        '''This method will extract the a2d samples from msg, to use in computations. msg["samp_sz"] will equal
          len(a2d) . This method then discards outliers by using dict slots (histogram ) The a2d_count that holds
          the most a2d_samples wins . Then a filter excludes samples that are more than 2 counts from the winner.
          This will leave a new list of a2d samples called "keep". "KEEP_SZ"  will be len(keep)  and
          DISCARD_SZ= SAMP_SZ - KEEP_SZ. Stats (mean, sd, vb,...) are computed from keep. The LSB is used to
          compute vm_mean and vm_sd.  vm_mean (a2d_mean*LSB) is used to lookup the value for vb.
          The error will be computed in svr_task_manager.compute_error(...)depending on TYPE.
          Returns a BMS tuple with augmented values: a2d_mean, vm_mean, vm_sd, vb,vin, error,
           "DISCARD_SZ", "KEEP_SZ  embedded. The entire BMS namedtuple is defined in
           database_interface_config.py. Currently, Fields are:  BMS_FIELDS =
           ("ID", "MSGID", "VERSION", "TIMESTAMP", "TYPE", "CHAN", "A2D_MEAN", "VM_MEAN",
           "VM_SD", "VB", "VIN", "ERROR", "SAMP_SZ", "DISCARD_SZ", "KEEP_SZ") '''
        #TODO 8: get k_factor to allow self.k to hold a value. It was breaking compute_stats. removed it for now 
        #print(f"entered svr_task_manager.compute_stats(msg)  with: the A2D samples ,LSB: {self.lsb},slope: {self.slope}, intercept: {self.intercepts}")
        chan = channel["CHAN"]
        a2d = channel["A2D"]
        samp_sz = len(a2d)
        #print(f" k_factor, k: {self.k}")
        #==========================
        slots={}
        for x in a2d:
            abin = slots.get(x, [])
            abin.append(x)
            slots[x]=abin
        # initialize low
        winning_score=1
        winner = 1
        for k,v in slots.items():
            if len(v) > winning_score:
                winner = k
                winning_score=len(v)
        print(f"winner a2d: {winner} with score of: {winning_score}")
        
        # Filter out outliers by keeping only counts within 2 counts of winner
        keep = [x for x in a2d if abs(x-winner) < 2 ]
        keep_sz=len(keep)
        discard_sz = samp_sz - keep_sz
        print(f"Doing stats on {len(keep)} a2d samples.")
        m = round(self.mean(keep),1)
        vrs= [(x-m)**2 for x in keep]
        sd =math.sqrt(self.mean(vrs))
        vin= channel["VIN"]
        print("hw3")
        vm_m= round(m*self.lsb, 4)
        print("hw4")
        vm_sd=round(sd*self.lsb, 8)
        print(f" slope: {self.slope[chan]} , intercept: {self.intercepts[chan]}")
        vb = round(vm_m*self.slope[chan]+self.intercepts[chan], 4)
        print("svr_task_mgr.compute_stats: hw2")
        print(f"hw6  vb: {vb} vin: {vin} type(vin): {type(vin)}")
        summary_dict  = {"ID":"",  "VERSION": self.version,
                                   "TIMESTAMP": channel["TIMESTAMP"],  
                                   "CHAN": chan, "A2D_MEAN": m, "VM_MEAN": vm_m, "VM_SD": vm_sd,
                                   "VB": vb, "VIN": vin, "ERROR" : None, "SAMP_SZ":samp_sz,
                                   "DISCARD_SZ": discard_sz, "KEEP_SZ" : keep_sz}
        print(f"summary_dict:  {summary_dict}")
        return summary_dict

    def lookup_chan_vm(self,  chan:int, vm:float):
        '''Given any legitimate value for vm (measured voltage) in a channel, chan,
          Returns the estimate of  vb (battery voltage), using interpolation.
          First  if vm is right on a boundary key, returns lut[boundary_key], then
          if vm is out of bounds, prints error statement and returns None,
          else interpolates vm to yield vb '''
        lut = self.luts[chan]
        lo_vm = min(lut.keys())
        hi_vm = max(lut.keys()) 
        if vm < lo_vm or vm > hi_vm:
            vm = None
        if vm == None:
            # vm was outside of allowable bounds... so vb is undefined...
            return None       
        #bracket vm by lut keys
        vhi = None
        vlo = None
        keys = list(lut.keys())
        for k in keys:
            if vm < k:
                vhi = k
                break
            else:
                vlo = k

        print(f"\tvlo: {vlo}, vm: {vm}, vhi: {vhi}")

        # --- Interpolation ---
        fract = (vm - vlo) / (vhi - vlo)     #fraction of the way from vm_lo to vm_hi
        vbhi = lut[vhi]
        vblo = lut[vlo]
        vb = round(vblo + fract * (vbhi - vblo), 4)      # vb= vin_low + fract * (vin_hi -  vin_lo)

        return vb
    
    def mean(self, alist):
         '''Returns the mean of a list of values. Used for simple mean and also variances)'''
         return sum(alist)/len(alist)
    
                    
