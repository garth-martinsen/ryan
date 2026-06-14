# file: database_interface.py. path: .../DEV/.../data
"""This class will retrieve and store in formation for the DataController which supplies info to the GUIs.
Transactions are used when writing to the db. Each fetch method will include the tuple_factory to be
used to convert the row values to a namedtuple: one of: [_Abbrev_namedtuple_factory, _Config_namedtuple_factory, _BMS_namedtuple_factory,_LUT_namedtuple_factory
Later it was determined to send raw tuples across the websocket and to apply the namedtuples in the client requesting the data
"""
import sqlite3
import time
import json
from database_interface_config import db_path, Config, Abbrev, BMS, LUT,CONFIG_FIELDS, BMS_FIELDS, Stats
from collections import OrderedDict
import re
import math
from typing import List

class DatabaseInterface:

    def __init__(self,app_id, version):
        self.db_path = db_path
        self.app_id =app_id
        self.version=version
        print(f"dbpath: {self.db_path} ")
        print(f"app_id: {self.app_id} ")
        print(f"version: {self.version}")
        self.cfgs: List[Config(),Config(), Config()]= [[],[],[]]
        self.luts :List[OrderedDict] =[OrderedDict(),OrderedDict(),OrderedDict()]
        self.lut_timestamps:List[str] = ["","",""]
        self.vd_fracts = {0: 0.688128140703518, 1:0.313249211356467, 2: 0.248189762796504}   #later, these should be set from Config record.
        self.msg = ""
       # TODO 9: should not set atype, bms_id in __init__ . Need to move dict or something...
        #atype="m"
        #bms_id=6
        cmds= dict()
#         cmds['150']=self. list_records( 0, atype)
#         cmds['152']=self. list_records( 1, atype)
#         cmds['154']=self. list_records( 2, atype)
#         cmds['156'] =self.get_a2d_samples(0, bms_id)
#         cmds['158']=self.get_a2d_samples(1, bms_id)
#         cmds['160']=self.get_a2d_samples(2, bms_id)
        cmds['310']=self.load_config(self.app_id,0,self.version)
        cmds['312']=self.load_config(self.app_id,1,self.version)
        cmds['314']=self.load_config(self.app_id,2,self.version)
        cmds['360']=self.luts[0]= self.get_lut( 0, self.version)
        cmds['362']=self.luts[1]= self.get_lut( 1, self.version)
        cmds['364']=self.luts[2]= self.get_lut( 2, self.version)
        cmds['370']=self.lut_timestamps[0]= self.get_lut_timestamp(0,self.version)
        cmds['372']=self.lut_timestamps[1]= self.get_lut_timestamp(1,self.version)
        cmds['374']=self.lut_timestamps[2]= self.get_lut_timestamp(2,self.version)
 #       cmds['101'] = self.save_measurement(self.msg)
        self.cmds=cmds
    

    def build_response(self, message):
        msg= f"Called dbi.build_response() with message: {message}"
        self.msg = json.loads(message)
        #print(f"msg.type:  {type(msg)}  msg:{msg}")
        response = f" {msg} TBD  DB: Work in progress..."
        # lookup in dict cmds to see what method to call:
        return_purpose=int(message) +1
        astring= self.cmds[message]
        response = f" request purpose: {message} response purpose: {return_purpose} , {astring}"
        print(response)
        return json.dumps(response)
    
    def _timestamp(self):
        """Returns local time as string, eg: YYYY-mm-DD HH:MM:SS. Note: for hour, min, sec less than 10, must have leading zero eg: 09:05:07"""
#        dt = time.localtime()
#      return f"{dt[0]}-{dt[1]}-{dt[2]}  {dt[3]}:{dt[4]}:{dt[5]}"  # YYYY-MM-DD  HH:mm:sec (dt[6] dow , dt[7] julian)
        return  time.strftime(' %X %x ')

    
    
#     def _Abbrev_namedtuple_factory(self, cursor, row):
#         """Returns row as a Abbrev_Record:
#         Abbrev = namedtuple("Abbrev",("id", "owner", "app_desc", "version_desc", "channel_id", "channel_desc"))
#         """
#         return Abbrev(*row)
# 
#     def _BMS_namedtuple_factory(self, cursor, row):
#         return BMS(*row)
# 
    def _LUT_namedtuple_factory(self, cursor, row):
        return LUT(*row)

#     def _Config_namedtuple_factory(self, cursor, row):
#         """Returns row as a  Config:  """
#         return Config(*row)


    def _create_cols_vals(self, msg):
        '''Removes fields not in BMS schema, Returns two lists with column names (cols) and values (vals) to facilitate inserts into db.'''
        # db table BMS has no column 'purpose' . ' type'  is used to reflect measurement/calibration instead. remove 'purpose' by pop
        # TODO 8: leave msgid in and update bms table to save it. chatgpt suggested this.
        #if "purpose" in msg:    msg.pop('purpose')
        #if "sender_id" in msg: msg.pop("sender_id")
        #if "msg_id" in msg:     msg.pop("msg_id")
        cols=[]
        vals=[]
        rejects=[]
        for k,v in msg.items():
            if k in BMS_FIELDS:
                cols.append(k)
                vals.append(v)
            else:
                rejects.append(k)
        print(" Rejected columns: ", rejects)
        return (cols, vals)

    def list_all_choices(self):
        """tuple_factory is the function that specifies the namedtuple to use in creating objects from *row
        For now it is: _Abbrev_namedtuple_factory"""
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        #self.cx.row_factory = self._Abbrev_namedtuple_factory
        select_str = "SELECT id, owner, app_desc, channel_id, channel_desc, version_desc  FROM CONFIG order by owner and channel_id;"
        records = []
        for row in cu.execute(select_str):
            records.append(row)
        # print("records: ", records)
        return records

    
    def load_config(self, aid,chan, version):
        """tuple_factory is the function that specifies the namedtuple to use in creating objects from *row
        For this select, it is one of: [_Abbrev_namedtuple_factory, _Config_namedtuple_factory,BMS]...TBD
        """
        cfg = []
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        #self.cx.row_factory = self._Config_namedtuple_factory
        cu = self.cx.cursor()
        select_str = f"SELECT * FROM CONFIG where  app_id = {aid} and chan = {chan} and version = {version};"
        print("select_str: ", select_str)
        # Each row is a channel.
        for row in cu.execute(select_str):
            print("row: ", row)
            cfg.append(Config(*row))
        self.cfgs[chan]=cfg
        return cfg
       # self.vd_fracts = cfg["vd_fracts"]
       

    #TODO 3 : Implement save_config(...) 
    def save_config(self, cfg_id:int, msg:Config):
        '''TBD... handles next version'''
        pass

    def _format_insert(self, insert_str):
        """quotes the keep list."""
        insert_str = insert_str.replace("[", "'[")
        insert_str = insert_str.replace("]", "]'")
        return insert_str
    
    def save_to_bms(self , msg):
        ''' Saves summary fields for both types ['m','c'] to the same database table, bms.Summary fields are :
 (ID | MSGID | VERSION | TIMESTAMP | TYPE | CHAN | A2D_MEAN | VM_MEAN |  VM_SD  |  VB  | VIN  |  ERROR  | SAMP_SZ | DISCARD_SZ | KEEP_SZ ).
 Also Saves the A2D samples embedded in msg to the A2D table with the bms_id to link the two tables.A2D Fields are: ( ID | BMS_ID | SAMPLES). where samples is a string
holding 64 int sample values. This can be expanded in length to have 128 samples etc.
arg msg is a dict loaded by ADC  with raw data and augmented by Server with  computations.
 json is used to convert from string dict. '''
       
        atype = msg["TYPE"]
        samples = msg.pop("SAMPLES")
        timestamp = msg['TIMESTAMP']  # this is from the ADC timestamp.
        chan = msg["CHAN"]
        vin = msg["VIN"]
        cols, vals = self._create_cols_vals(msg)      #should only contain the summary fields.
        print(f"called dbi. save_measurement() with cols: {cols} values: {vals} ")
        bms_insert_str = f"insert into BMS {tuple(cols)} values {tuple(vals)}; "

        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        cu.execute(bms_insert_str)
        res = cu.execute('select max(id) from bms')
        bms_id=  res.fetchone()[0]
        print(f"bms_id: {bms_id}")
        a2d_insert_str = f"insert into A2D values(NULL, {bms_id}, '{samples}')"
        print(f"a2d_insert_str: {a2d_insert_str}")
        cu.execute(a2d_insert_str)
        self.cx.commit()
        return (cols, vals)
 '''
ID,OWNER,APP_ID,APP_DESC,CHAN,CHAN_DESC,VERSION,VERSION_DESC,TIMESTAMP,TEMPC,ADC_FSR,ADC_STEPS,ADC_SAMPLE_RATE,C1,R1,R2,VD_FRACT,LUT_CALIBRATED,LUT_TS
5,GM,1,Development    ,0,3-4.5V circuit chan(0),3,PCB2,2026-6-02_18:44:20:00,25.4,4.096,32768,64,1.0e-07,101100.0,303700.0,0.750247035573123,0,2026-6-02_18:44:20:00
6,GM,1,Develop    ment,1,6-9V circuit chan(1),3,PCB2,2026-6-02_18:44:20:00,25.4,4.096,32768,64,1.0e-07,222200.0,111800.0,0.334730538922156,0,2026-6-02_18:44:20:00
7,GM,1,Developmen    t,2,9-13.5 V circuit chan(2),3,PCB2,,2026-6-02_18:44:20:00,25.4,4.096,32768,64,1.0e-07,301400.0,100700.0,0.250435215120617,0,2026-6-02_18:44:20:00
''' 
    def list_records(self, chan, atype):
        ''' Returns a list<records> of type atype.'''
        records = []
        select_str = f" select * from BMS where chan={chan} and type = '{atype}' ;  "
        print(f"select _str: {select_str}")
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
       # self.cx.row_factory = self._BMS_namedtuple_factory
        cu = self.cx.cursor()
        for row in cu.execute(select_str):
            records.append(row)
        return records
    

    def get_a2d_samples(self, bms_id):
        ''' retrieves the a2d samples as a list from tableA2D in order to analyze sample problems'''
        records=[]
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        select_str = f"select samples from A2D where bms_id = {bms_id};"
        print("select_str: ", select_str)
        for row in cu.execute(select_str):
            records.append(row)
        lst=list(records[0])
        a2d=json.loads(lst[0])
        return a2d
 
    def get_lut_row(self, chan, vm):
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        select_str = f"select id,vm,vin, version from luts where chan = {chan} and version= {self.version} and vm={vm};"
        # print("select_str: ", select_str)
        res = cu.execute(select_str)
        return res.fetchone()
        
    def get_lut(self, chan,version):
        records=[]
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        #self.cx.row_factory = self._LUT_namedtuple_factory
        cu = self.cx.cursor()
        select_str = f"select id,vm,vin from luts where chan = {chan} and version= {self.version};"
        print("select_str: ", select_str)
        for row in cu.execute(select_str):
            records.append(row)
        return self.lut_as_od(chan, records)

    def get_lut_timestamp(self, chan, version):
        timestamp = ""
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        select_str = f"select LUT_TS from CONFIG where chan={chan} and version={self.version}";
        res= cu.execute(select_str)
        timestamp = res.fetchone()[0]
        print(timestamp)
        return timestamp
    
    def update_lut_timestamp(self, chan, version):
        '''Called when any lut is updated. It updates the lut_timestamp in the config table.'''
        timestamp = self._timestamp()
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        update_str = f"update config set LUT_TS ='{timestamp}'  where chan={chan}";
        print(f"update_str: {update_str}")
        cu.execute(update_str)
        self.cx.commit()
       
 
    
     #TODO 2: Implement and Test update_lut_vin(...)
    def update_lut_pair(self, chan, _id, vm, vin):
        '''updates a single vin value for a given id'''
        ts = self._timestamp()
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        cfg_update_str = f" UPDATE Config  set LUT_TS ='{ts}' where id = {_id};"
        lut_update_str = f"Update LUTS set vm={vm} , vin={vin} where id={_id} "
        print("cfg_update_str: ", cfg_update_str)
        cu.execute(cfg_update_str)
        cu.execute(lut_update_str)
        self.update_lut_timestamp(chan, self.version)
        self.cx.commit()

    
    #TODO 5: Copy lut_as_od to the gui_client.py module if cannot send od across the wire.
    def lut_as_od(self, chan, lut):
        '''lut is any of lut0, lut1, lut2 and is a list of str. This method uses re to findall strings which are decimal numbers.
        Method takes in list returned by db, converts it into an OrderedDict... and stores it in luts[chan]'''
        vm=[]
        vin=[]
        _id=[]
        cnt=0
        p=re.compile('\\d+\\.\\d+')  # pattern is one or more digits, a decimal point, one or more digits eg: 2.345
        lst=p.findall(str(lut))  # l is list of str( decimal number)
        # l consists of vm, vin , vm, vin,... Must push them into vm and vin lists as floats.
        for x in lst:
            if cnt%2==0:
                vm.append(float(x))
            else:
                vin.append(float(x))
            cnt +=1
        #zipping the two lists will produce a zip which can be used as arg to instantiate the OrderedDict.
        zp = zip(vm,vin)
        #print(f" vm: {vm}, vin: {vin} zipped: {zp}")
        od=OrderedDict(zp)
        print(f" od: {od}")
        self.luts[chan]=od
        return od
 
 # TODO 10: stats() method should be implemented elsewhere...
    def stats(self, chan:int, samples:list[int]):
        ''' Computes m,sd,vm,vb, from  samples and Returns a Stats namedtuple'''
        print(f"type(samples): {type(samples)} ")
        m=int(round(sum(samples)/len(samples),3))
        vars = [(x-m)*(x-m) for x in samples]
        lsb=4.095/32768
        sd = math.sqrt(sum(vars)/len(vars))    # for a2d counts
        vm=round(lsb*m,4)
        vm_sd=round(lsb*sd,6)                         # converted to voltage
        vbe = self.lookup_chan_vm(chan, vm )
        vb = round( vbe, 4 )
        print(" a2d_mean, vm_mean, vm_sd, vb estimate")
        return Stats(m, vm , vm_sd, vb)

    def matchesboundary(self, chan:int, vm:float, version:int) :
        '''Returns tuple(vm, lut). Vm is None if outside of allowed boundary limits, Returns vm if vm is within tol of first or last key. tol is 1/2* vinstep * vd_fract'''
     
     #TODO 7: DONE:  Remove the tolerance on border vms, too complex. Just enforce the actual boundaries.
        lut=self.luts[chan]
        keys = list(lut.keys())
        minkey = keys[0]
        maxkey = keys[-1]
        print(f"\t bounds for chan {chan}: {minkey}, {maxkey}")
        vinstep = 0.1            # all luts have vin in 0.1V steps.
        tol = vinstep/2*self.vd_fracts[chan]    # Design Rule: Tol = the vm for 1/2 vin step  
        #allowable vm values to set vm = minkey or maxkey depending...
        lo_tol = minkey - tol
        hi_tol = maxkey + tol
        if vm < lo_tol or vm > hi_tol:
             print( f"Error: {minkey} <= vm:{vm} <= {maxkey} violated. Returning None for vm")
             return (None, lut)
        else:
            # if vm is close enough to minkey or maxkey, set vm to minkey or maxkey depending
            vmr=None
            if  lo_tol < vm < keys[1]:
                vmr = minkey
            elif keys[-2] < vm < hi_tol:
                vmr = maxkey
            else:
                #passed in vm is inside of lut boundaries so it can be interpolated.
                vmr = vm
        return (vmr, lut)
     #TODO 11: lookup_chan_vm() should be implemented elsewhere...       
    def lookup_chan_vm(self,  chan:int, vm:float):
        '''Given any legitimate value for vm (measured voltage) in a channel, chan,  return the estimate of vb (battery voltage), using interpolation.
        First  if vm is close enough to a boundary key, returns lut[boundary_key], then if vm is out of bounds, prints error statementand returns None,
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

    def check_bms_id_in_a2d(self):
        '''Returns the id of the last bms record and the bms_id of the last A2D record. Good to ensure sync.'''
        a2d_select_str='select max(bms_id)  from A2D'
        bms_select_str = 'select max(id) from BMS'
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        print(f"a2d_select_str: {a2d_select_str}")
        print(f"bms_select_str: {bms_select_str}")
        res=cu.execute(a2d_select_str)
        bms_id = res.fetchone()[0]
        res=cu.execute(bms_select_str)
        _id = res.fetchone()[0]
        print(f"Returning bms.id = {_id} and a2d.bms_id = {bms_id}")
        return (_id, bms_id) 
        
        

        
