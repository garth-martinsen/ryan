# file: svr_task_manager.py  Offloads most of the work from the bms_async_server:  routes msgs,
# returns json-worthy, correct namedtuple. The bms_async_server has requirements: 1. manage client connections,
# 2. receive json msgs,  restore python objects by json.loads(...), 2. delegate msg_processing to svr_msg_processor ,
# 3.. send json-appropriate msgs to correct async_client.

from common import bms_config
from common.models.voltage_row import VoltageRow
from dataclasses import asdict
from .database_interface import DatabaseInterface
import json
from .database_interface_config import APP_CONFIG, BMS, GPS_FIELDS
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
        self.get_estimator_parms()
        self.load_luts()
        # TODO 5: get allowance from app_config or chan_config...For now KLUGE it and just assign it.
      # allowance = how much can a measued_vb differ from the predicted_vb and still be reportable? 
        self.allowance=500e-7    
        self.measurements = {}
        self.last_vb = {0:4.044, 1: 7.89, 2: 11.95}
        self.last_vb_time = {0: 1785030326.0, 1: 1785030337.0, 2: 1785030347.0 }
        #TODO: load slope and intercepts from CHANNELS table via dbi
        '''│ 1.33289430358907 │ 0.024164327787965  │
           │ 2.98747763864043 │ 0.0498818752307106 │
           │ 3.99304865938431 │ 0.0641294273419395 │ '''
        self.slope=[1.33289430358907, 2.98747763864043,3.99304865938431]
        self.intercepts=[0.024164327787965,0.0498818752307106,0.0641294273419395]
        self.get_app_config()
        for chan in range(3):
            self.get_chan_config(chan)
        self.load_handlers_dict()

    # TODO 4: Augment handlers_dict with code+1 msgs coming into svr...

    def load_handlers_dict(self):
        handlers_dict    = dict()
        # handlers_dict[0] = self.client_register_with_server                      # ( [] )   # handled by bms_asyncio_svr...
        handlers_dict[2] = self.request_time_sync                                # ( [] )
        handlers_dict[4] = self.dbi.get_max_meas_id                              # ( [] )
        handlers_dict[10]= self.dbi.get_app_config                              # ( )
        handlers_dict[12]= self.dbi.update_app_config                             # ( [cfg_id, msg:Config] )
        handlers_dict[20]= self.dbi.get_chan_config                             # ( [chan] )
        handlers_dict[22]= self.dbi.update_chan_config                            # ( [chan] )
        handlers_dict[30]= self.forward_to_ADC                                  # ( [msg, clients] )
        handlers_dict[31]= self.process_adc_measurement_report                  # ( [measurement_report] )
        handlers_dict[32]= self.start_periodic_voltage_measurements             # ( [period, reps] )
        handlers_dict[40]= self.forward_to_ADC                                  # ( [msg, clients] )
        handlers_dict[41]= self.process_adc_measurement_report                  # ( [measurement_report ] )
        handlers_dict[42]= self.start_periodic_calibrations                     # ( [ period, reps, [vin0,vin1,vin2] ] )
        handlers_dict[50]= self.dbi.save_to_bms                                 # ([ bms: BMS ])
        handlers_dict[52]= self.dbi.list_bms                                    # ([ chan, type])
        handlers_dict[54]= self.dbi.get_bms_a2d_samples                         # ([ bms_id])
        handlers_dict[60]= self.dbi.get_ah_total                                # ( [ ] )
        handlers_dict[62]= self.dbi.save_amp_hrs                                # ( [ ] )
        handlers_dict[62]= self.dbi.get_last_amp_hrs                            # ( [ ] )
        handlers_dict[66]= self.dbi.delete_test_amp_hrs                         # ( [ ] )
        handlers_dict[70]= self.dbi.get_lut                                     # ( [chan] )
        handlers_dict[72]= self.dbi.get_lut_item                                # ( [chan, vin] )
        handlers_dict[74]= self.dbi.update_lut_pair                             # ([  _id,  vm,  vin] )    
        handlers_dict[76]= self.dbi.get_lut_timestamp                           # ([ chan ])
        handlers_dict[78]= self.dbi.update_lut_timestamp                        # ([  _id,  vm,  vin] )
        handlers_dict[80]= self.dbi.get_estimator_parms                         # ([])
        handlers_dict[82]= self.dbi.update_estimator_parms                      # ([])
        handlers_dict[90]= self.dbi.save_GPS_output                             # ([?])
        handlers_dict[90]= self.dbi.get_GPS_Output                              # ([?])
        self.handlers_dict=handlers_dict

    def call_function( self, code, argslist):
        print(f" code: {code}   function: {self.funct_dict[code].__name__} argslist: {argslist}")
        return self.handlers_dict[code]( *argslist )

    def save_GPS_output(self, code, argslist):
        '''Calls DBI to save GPS output'''
        self.dbi.save_GPS_output( argslist)

    def request_time_sync(self):
        '''Returns a timestamp that clients can use to synchronize their timers...'''
        return time.localtime()

    def start_periodic_voltage_measurements(self, code, arglist):
        '''Just forward msg to ADC...'''
        self.forward_to_ADC(code, arglist)

    def start_periodic_calibrations (self, code, argslist):
        '''Just forward msg to ADC...'''
        self.forward_to_ADC(code, arglist)

    def update_estimator_parms(self, code, argslist):
        '''Calls dbi to update slope and intercept.'''
        self.dbi.update_estimator_parms(code, argslist)
 
    async def forward_to_ADC(self, code, argslist):
        '''Adds msgid, sends to ADC client, acks Gui...'''
        #TODO 6: Move msgid from bms_asyncio_svr to here...
        clients = argslist["clients"]
        msg=argslist["msg"]
        if "msg"["SENDER"]=="GUI" and msg["RECEIVER"] == "ADC":
            msgid = self.dbi.next_msgid()
            msg["MSGID"]=msgid
            #print(f" msgid stamped msg: {msg}")
        await self.send_to_client("ADC", msg, clients)
        gui_ack = {"CODE": code, "SENDER":"SVR", "RECEIVER":"GUI","STATUS":"YOUR MESSAGE WAS FORWARDED TO ADC","MSGID":msg["MSGID"]}
        await self.send_to_client("GUI", gui_ack, clients)

    async def process_adc_measurement_report(self, msg):
        '''Tests for Reportability. Removes outliers from a2d list to get KEEP, computes mean and sd of KEEP, 
        Computes/looks up estimated battery voltage, vb. Computes error if vin is available. 
        Persists in BMS, A2D, AMP_HRS tables. Formats for GUI presentation, Sends to GUI.'''

        reportable= self.test_reportability(msg)
        stats_result_dict = self.compute_stats(msg)
        meas_id = msg["MEAS_ID"]
        print(f"result type {type(stats_result_dict)}  stats_result_dict: {stats_result_dict}")
        # TODO 3: FINISH 101 201 ... format for needed cols for BMS table pass in correct arglist...
        #("ID", "MSGID", "VERSION", "TIMESTAMP", "TYPE", "CHAN", "A2D_MEAN", "VM_MEAN", "VM_SD", "VB", "VIN", "ERROR", "SAMP_SZ", "DISCARD_SZ", "KEEP_SZ")
        bms_dict_to_store = {"ID" : "", "MSGID":msg["MSGID"], "VERSION": msg["VERSION"],
                               "TIMESTAMP": msg["TIMESTAMP"], "MEAS_ID": meas_id, "TYPE" : msg["TYPE"], "CHAN" : msg["CHAN"], 
                               "A2D_MEAN" : stats_result_dict["A2D_MEAN"], "VM_MEAN" : stats_result_dict["VM_MEAN"], 
                               "VM_SD" :stats_result_dict["VM_SD"], "VB" :stats_result_dict["VB"],
                               "VIN" : msg["VIN"], "ERROR" :stats_result_dict["ERROR"], "SAMP_SZ" : msg["SAMP_SZ"],
                               "DISCARD_SZ" : stats_result_dict["DISCARD_SZ"], "KEEP_SZ" : stats_result_dict["KEEP_SZ"],
                               "A2D" : msg["A2D"]}
        print(f"bms_dict_to_store for  BMS table: type: {type(bms_dict_to_store)} msg: { [bms_dict_to_store]} ")
        bms_id = self.dbi.save_to_bms( bms_dict_to_store  )
        lst = self.measurements.get(meas_id, [])
        lst.append(VoltageRow(bms_id, timestamp, _type, chan, vb, ))
        self.measurements[meas_id]= lst
        if measurement[meas_id]: 
            rows = [
            VoltageRow(...),
            VoltageRow(...),
            VoltageRow(...),
            ]
        bms_dict_to_store["ID"]=bms_id
        bms_dict_to_store.pop("A2D")
        # Send the formatted msg to the GUI
        await self.send_to_client("GUI", bms_dict_to_store, clients)

    def get_app_config(self):
        cfg = self.dbi.get_app_config()
        app_config = APP_CONFIG(*cfg)
        print(f"app_config: {app_config}")
        FSR=app_config.ADC_VOLT_FSR
        STEPS = app_config.ADC_STEPS
        self.lsb = FSR/STEPS

    def get_chan_config(self, chan):
        cfg= self.dbi.get_chan_config(chan) 
        self.chan_config[chan] = cfg;
 #TODO: finish chan_config and TEST it.

    def adc_setup_periodic(self, functions_dict, argslist):
        print("Not yet implemented TBD")

    def load_luts(self):
        luts=[]
        luts.append(self.dbi.get_lut(0))
        luts.append(self.dbi.get_lut(1))
        luts.append(self.dbi.get_lut(2))
        self.luts=luts

    def get_estimator_parms(self):
        self.estimator_parms = self.dbi.get_estimator_parms()               

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
        '''Sends msg from GUI_client, along with MSGID to ADC_client. msg includes: vins, type='c', chan'''
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

    #TODO 3: Replace if code in ... with self.call_function(self, code, arglist)...

    async def create_and_schedule_tasks (self, loop, msg, clients ):
        '''Based on receiver, sender and code fields, route msg to a method where it can be processed.
          The tasks will be to perform async methods including send_to_client(...) '''
        print(f"Entered method svr_task_mgr.create_and_schedule_tasks with msg of type:{type(msg)}")
        try:
            print(f"msg: {msg}")
            code = int(msg["CODE"])
            argslist = msg["ARGLIST"]
            print("reached : hw1")       
            self.call_function(code, argslist)

                
              # all of the even codes > 300 from GUI will be tasked to the dbi and returned to the gui_client with code=code+1.
            if code > 300 and code%2 == 0:
                print(f"Request msg: { msg}")
                arglist=msg["ARGLIST"]
                print(f" arglist: {arglist}")
                data = self.dbi.call_function(code, arglist)
                response = {"CODE":code+1, "RECEIVER": 'GUI', "SENDER": "SVR", "MSGID": msg["MSGID"], "DATA": data}
                #print(f" dbi data: {data}")
                if code == 302:
                    tm= self.dbi.call_function(302, [ ] )
                    response = {"RECEIVER" : "ADC", "SENDER": "SVR", "CODE": 303, "TIME_SYNC": tm}
                    if msg["SENDER"] =="ADC":
                        await self.send_to_client("ADC" ,response, clients)
                    else:
                        await self.send_to_client("GUI" ,response, clients)

        except  Exception as e:
            print("Error:", e)
            print("file: " , e.__traceback__.tb_frame.f_code.co_filename)
            print("line no: " , e.__traceback__.tb_lineno)
            
    def compute_stats(self, msg):
        '''This method will extract the a2d samples from msg, to use in computations. msg["samp_sz"] will equal
          len(a2d) . This method then discard outliers by using dict slots (histogram ) The a2d_count that holds
          the most a2d_samples wins . Then a filter excludes samples that are more than 5 counts from the winner.
          This will leave a new list of a2d samples called "keep". "KEEP_SZ"  will be len(keep)  and
          DISCARD_SZ= SAMP_SZ - KEEP_SZ. Stats are computed from keep: mean, sd. The LSB is used to
          compute vm_mean and vm_sd.  vm_mean (a2d_mean*LSB) is used to lookup the value for vb.
          If msg['type'] == 'c', (calibration) the msg embedded code will be 200  and will have embedded vin .
          The error is computed (error = vin-vb)
          Returns a BMS tuple with augmented values: a2d_mean, vm_mean, vm_sd, vb,vin, error,
           "DISCARD_SZ", "KEEP_SZ  embedded. The entire BMS namedtuple is defined in
           database_interface_config.py. Currently, Fields are:  BMS_FIELDS =
           ("ID", "MSGID", "VERSION", "TIMESTAMP", "TYPE", "CHAN", "A2D_MEAN", "VM_MEAN",
           "VM_SD", "VB", "VIN", "ERROR", "SAMP_SZ", "DISCARD_SZ", "KEEP_SZ") '''
 #TODO get k_factor to allow self.k to hold a value. It was breaking compute_stats. removed it for now 
        #print(f"entered svr_task_manager.compute_stats(msg)  with: the A2D samples ,LSB: {self.lsb},slope: {self.slope}, intercept: {self.intercepts}")
        chan = msg["CHAN"]
        a2d = msg["A2D"]
        samp_sz = len(a2d)
        #print(f" k_factor, k: {self.k}")
        #==========================
        slots={}
        for x in a2d:
            abin = slots.get(x, [])
            abin.append(x)
            slots[x]=abin
        # initialize low
        print("svr_task_mgr.compute_stats: hw2")
        winning_score=1
        winner = 1
        for k,v in slots.items():
            if len(v) > winning_score:
                winner = k
                winning_score=len(v)
        print(f"winner a2d: {winner} with count of: {winning_score}")
        
        # Filter out outliers by keeping only counts within 5 counts of winner
        keep = [x for x in a2d if abs(x-winner) < 5 ]
        keep_sz=len(keep)
        discard_sz = samp_sz - keep_sz
        print(f"Doing stats on {len(keep)} a2d samples.")
        m = self.mean(keep)
        vrs= [(x-m)**2 for x in keep]
        sd =math.sqrt(self.mean(vrs))
        vin= msg["VIN"]
        print("hw3")
        vm_m= round(m*self.lsb, 4)
        print("hw4")
        vm_sd=round(sd*self.lsb, 8)
        print(f" slope: {self.slope[chan]} , intercept: {self.intercepts[chan]}")
        vb = round(vm_m*self.slope[chan]+self.intercepts[chan], 4)
        print(f"hw6  vb: {vb} vin: {vin} type(vin): {type(vin)}")
        error = round((float(vin) - vb), 6)
        summary_dict  = {"ID":"", "MSGID":msg["MSGID"], "VERSION": self.version,
                                      "TIMESTAMP": msg["TIMESTAMP"], "TYPE" : msg["TYPE"],
                                      "CHAN": chan, "A2D_MEAN": m, "VM_MEAN": vm_m, "VM_SD": vm_sd,
                                      "VB": vb, "VIN": vin, "ERROR" : error, "SAMP_SZ":samp_sz,
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
    
