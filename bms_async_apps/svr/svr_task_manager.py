# file: svr_task_manager.py  Offloads most of the work from the bms_async_server:  routes msgs,
# returns json-worthy, correct namedtuple. The bms_async_server has requirements: 1. manage client connections,
# 2. receive json msgs,  restore python objects by json.loads(...), 2. delegate msg_processing to svr_msg_processor ,
# 3.. send json-appropriate msgs to correct async_client.
from .database_interface import DatabaseInterface
import json
from .database_interface_config import APP_CONFIG, BMS
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
        self.get_estimator_parms()
        self.load_luts()
        self.load_config()
        self.load_functions_dict()
        
        
    def load_functions_dict(self):
        functions_dict  = dict()
       # functions_dict[101]= self.compute_store_send                 # ([msg, receiver, ])
        #functions_dict[201]= self.compute_store_send                 # ([msg, receiver, ])
        self.functions_dict = functions_dict
       
    def load_config(self):
        cfg = self.dbi.get_app_config()
        app_config = APP_CONFIG(*cfg)
        FSR=app_config.ADC_FSR
        STEPS = app_config.ADC_STEPS
        self.lsb = FSR/STEPS
       # self.k = app_config.K_FACTOR      # wrong. k_factor is a channel attribute.
 
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
        '''Sends msg from GUI_client, along with MSGID to ADC_client. msg includes: vin, type='c', chan'''
        await self.send_to_client("ADC", msg, clients)
  
    async def adc_measure(self):
        '''Sends msg from GUI_client, along with MSGID to ADC_client. '''
        await self.send_to_client("ADC", msg, clients)
  

    async def create_and_schedule_tasks (self, loop, msg, clients ):
        '''Based on receiver, sender and code fields, route msg to a method where it can be processed.
          The tasks will be to perform async methods including send_to_client(...) '''
        print(f"Entered method svr_task_mgr.create_and_schedule_tasks with msg of type:{type(msg)}")
        try:
            print(f"msg: {msg}")
            code = int(msg["CODE"])
            print("reached : hw 1")       
            # for codes: 100,174,200 ,msg,with embedded msigid is forwarded to the ADC_client .
            if code in [100,174,200, 274]:
                await self.send_to_client("ADC", msg, clients)
                response = {"CODE": code, "SENDER":"SVR", "RECEIVER":"GUI","STATUS":"YOUR MESSAGE WAS FORWARDED TO ADC","MSGID":msg["MSGID"]}
                await self.send_to_client("GUI", response, clients)
            if code in [101,201]:
                stats_result_dict = self.compute_stats(msg)
                
                print(f"result type {type(stats_result_dict)}  stats_result_dict: {stats_result_dict}")
                # TODO 3: FINISH 101 201 ... format for needed cols for BMS table pass in correct arglist...
                 #("ID", "MSGID", "VERSION", "TIMESTAMP", "TYPE", "CHAN", "A2D_MEAN", "VM_MEAN", "VM_SD", "VB", "VIN", "ERROR", "SAMP_SZ", "DISCARD_SZ", "KEEP_SZ")
                store_to_bms_dict= {"ID" : "", "MSGID":msg["MSGID"], "VERSION": msg["VERSION"], "TIMESTAMP": msg["TIMESTAMP"],
                                    "TYPE" : msg["TYPE"], "CHAN" : msg["CHAN"], "A2D_MEAN" : stats_result_dict["A2D_MEAN"],
                                     "VM_MEAN" : stats_result_dict["VM_MEAN"], "VM_SD" :stats_result_dict["VM_SD"], "VB" :stats_result_dict["VB"],
                                     "VIN" : msg["VIN"], "ERROR" :stats_result_dict["ERROR"], "SAMP_SZ" : msg["SAMP_SZ"],
                                     "DISCARD_SZ" : stats_result_dict["DISCARD_SZ"], "KEEP_SZ" : stats_result_dict["KEEP_SZ"],
                                     "A2D" : msg["A2D"]}
                print(f"store_to_bms_dict for  BMS table: type: {type(store_to_bms_dict)} msg: { [store_to_bms_dict]} ")
                bms_id = self.dbi.save_to_bms( store_to_bms_dict  )
                # send to GUI  client the 'store_to_bms_dict'  adding bms_id and removing "A2D" 
                store_to_bms_dict["ID"]=bms_id
                store_to_bms_dict.pop("A2D")
                await self.send_to_client("GUI", store_to_bms_dict, clients)
                
              # all of the even codes > 300 will be tasked to the dbi and returned to the gui_client with code=code+1.
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
  
        print(f"entered svr_task_manager.compute_stats(msg)  with: the A2D samples ,LSB: {self.lsb}, k: {self.k} , vd_fract: {self.vd_fracts}")
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
        vb = round(vm_m*self.slope[chan]+self.intercept[chan], 4)
        print(f"hw6  vb: {vb} vin: {vin} type(vin): {type(vin)}")
        error = round((float(vin) - vb), 6)
        summary_dict  = {"ID":"", "MSGID":msg["MSGID"], "VERSION": self.version,
                                      "TIMESTAMP": msg["TIMESTAMP"], "TYPE" : msg["TYPE"],
                                      "CHAN": chan, "A2D_MEAN": m, "VM_MEAN": vm_m, "VM_SD": vm_sd,
                                      "VB": vb, "VIN": vin, "ERROR" : error, "SAMP_SZ":samp_sz,
                                      "DISCARD_SZ": discard_sz, "KEEP_SZ" : keep_sz}
        print(f"summary_dict:  {summary_dict}")
        return summary_dict

         
#===========================
        
#         vin = msg["VIN"]
#         m=self.mean(samples)
#         vrs = 
#         sd = math.sqrt(self.mean(vrs))
#         #discard outliers... may need to adjust k . To start, pass in k=3
#         keep = [x for x in samples if abs(x-m) < (sd*self.k)]
#         
#         #final pass: do stats on keep instead of all samples
#         keep_sz=len(keep)
#         discard_sz = samp_sz - keep_sz
#         print(f"samp_sz: {samp_sz}  keep_sz: {keep_sz}  discard: {len(samples)- keep_sz}")
#         print("hw4")
#         m = round(self.mean(keep), 4)
#         vrs =  [(x-m)*(x-m) for x in keep]
#         sd = math.sqrt(self.mean(vrs))
#         vm= round(m*self.lsb, 4)
#         print("hw5")
#         vm_sd=round(sd*self.lsb, 8)
#         vb = round(vm/self.vd_fracts[chan], 4)
#         print(f"hw6  vb: {vb} vin: {vin} type(vin): {type(vin)}")
#         error = round((float(vin) - vb), 6)
#         print("hw7")
#      
#         store_to_bms_dict = {"ID":"", "MSGID":msg["MSGID"], "VERSION": self.version, "TIMESTAMP": msg["TIMESTAMP"], "TYPE" : msg["TYPE"],
#                        "CHAN": chan, "A2D_MEAN": m, "VM_MEAN": vm, "VM_SD": vm_sd, "VB": vb, "VIN": vin, "ERROR" : error, "SAMP_SZ":samp_sz, "DISCARD_SZ": discard_sz, "KEEP_SZ" : keep_sz}
#         print(f"store_to_bms_dict:  {store_to_bms_dict}")
#         return store_to_bms_dict

    def lookup_chan_vm(self,  chan:int, vm:float):
        '''Given any legitimate value for vm (measured voltage) in a channel, chan,
          Returns the estimate of  vb (battery voltage), using interpolation.
          First  if vm is right on a boundary key, returns lut[boundary_key], then
          if vm is out of bounds, prints error statement and returns None,
          else interpolates vm to yield vb '''
        vm, lut  = self.matchesboundary(chan, vm, self.version)
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
    
    def matchesboundary(self, chan:int, vm:float, version:int) :
        '''Returns tuple(vm, lut). Vm is None if outside of allowed boundary limits, Returns vm if vm is within tol of first or last key.'''
     
        lut=self.luts[chan]
        keys = list(lut.keys())
        minkey = keys[0]
        maxkey = keys[-1]
        #print(f"\t bounds for chan {chan}: {minkey}, {maxkey}")
        vinstep = 0.1            # all luts have vin in 0.1V steps.
        tol = vinstep/2*self.vd_fracts[chan]    # Design Rule: Tol = the vm for 1/2 vin step  
        #allowable vm values to set vm = minkey or maxkey depending...
        lo_tol = minkey - tol
        hi_tol = maxkey + tol
        if vm < lo_tol or vm > hi_tol:
            print( f"Error: {minkey} <= vm:{vm} <= {maxkey} violated. Returning None for vm")
            return (None, lut)
        else:
            # if vm is equal to minkey or maxkey, set vm to minkey or maxkey depending
            vmr=None
            if  lo_tol < vm < keys[1]:
                vmr = minkey
            elif keys[-2] < vm < hi_tol:
                vmr = maxkey
            else:
                #passed in vm is inside of lut boundaries so it can be interpolated.
                vmr = vm
        return (vmr, lut)
                    
