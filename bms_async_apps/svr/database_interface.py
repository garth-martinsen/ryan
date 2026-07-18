# file: database_interface.py. path: .../DEV/.../data
"""This class will retrieve and store in formation for the DataController which supplies info to the GUIs.
Transactions are used when writing to the db. Each fetch method will include the tuple_factory to be
used to convert the row values to a namedtuple: one of: [_Abbrev_namedtuple_factory, _Config_namedtuple_factory, _BMS_namedtuple_factory,_LUT_namedtuple_factory
Later it was determined to send raw tuples across the websocket and to apply the namedtuples in the client requesting the data
"""
import sqlite3
import time
import datetime
import json
from .database_interface_config import db_path, APP_CONFIG,CHAN_CONFIG,  BMS, LUT,APP_CONFIG_FIELDS, CHAN_CONFIG_FIELDS, BMS_FIELDS, Stats, funct_desc

from collections import OrderedDict, namedtuple
import re
import math
from typing import List
#import asyncio

# ID | APP_ID | VERSION | CHAN |   VM   | VIN  |
LUT_ITEM = namedtuple("LUT_ITEM", ("ID", "APP_ID", "VERSION", "CHAN", "VM", "VIN", ))
 
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
        self.slope=[]
        self.intercept = []
        self.msg = ""
        self.funct_dict = self.create_function_dict()
        self.funct_desc = funct_desc

    def create_function_dict(self):
            funct_dict  = dict()
            funct_dict[300]= self.save_config                                     # ( [cfg_id, msg:Config] )
            funct_dict[302]= self. sync_time                                       # ( [] )
            funct_dict[310]= self.get_app_config                               # ( )
            funct_dict[312]= self.get_chan_config                        # ( [chan] )
            funct_dict[320]= self.save_to_bms                                   # ([ bms: BMS ])
            funct_dict[330]= self.list_bms                                           # ([ chan, type])
            funct_dict[340]= self.get_bms_a2d_samples                  # ([ bms_id])
            funct_dict[350]= self.get_lut                                              # ( [chan] )
            funct_dict[352]= self.get_lut_item                                     # ( [chan, vin] )
            funct_dict[360]= self.get_lut_timestamp                           # ([ chan ])
            funct_dict[370]= self.update_lut_pair                               # ([  _id,  vm,  vin] )    
            funct_dict[380]= self.update_lut_timestamp                    # ([  _id,  vm,  vin] )
            funct_dict[390]= self.get_estimator_parms                                  #([])
            return funct_dict
            
    def call_function( self, code, argslist):
        print(f" code: {code}   function: {self.funct_dict[code].__name__} argslist: {argslist}")
        return self.funct_dict[code]( *argslist )
    
    def get_column_headers(self, table_name):
        headers=[]
        cu = self.get_cursor()
        select_str = f" select * from {table_name}"
        data = cu.execute(select_str)
        for column in data.description:
            headers.append(column[0])
        return headers
    
    def get_schemas(self):
        records=[]
        cu=self.get_cursor()
        str_select = "select sql from sqlite_schema where type='table'"
        for row in cu.execute(str_select):
            records.append(row)
        print(f" schemas: {records}")
        return records
        
    def sync_time(self):
        tlt=time.localtime()
        #reformat for micropython 
        uptlt = (tlt[0],tlt[1],tlt[2], tlt[6], tlt[3],tlt[4], tlt[5],0)
        return json.dumps(uptlt)
    
    def build_response(self, message):
        msg= f"Called dbi.build_response() with message: {message}"
        self.msg = json.loads(message)
        #print(f"msg.type:  {type(msg)}  msg:{msg}")
        response = f" {msg} TBD  DB: Work in progress..."
        # lookup in dict cmds to see what method to call:
        return_purpose=int(message) +1
        astring= self.cmds[message]
        response = f" request purpose: {message} response purpose: {return_purpose} , {astring}"
        #print(response)
        return json.dumps(response)
    
    def _timestamp(self):
        '''Returns tuple   eg:  ime.struct_time(tm_year=2026, tm_mon=6, tm_mday=24, tm_hour=22, tm_min=17, tm_sec=35, tm_wday=2, tm_yday=175, tm_isdst=1)'''
        return  time.time()

    def human_timestamp(self, tm: float):
        ''' Returns human-readable string  eg: '2026-06-20 10:59:01' '''
        return datetime.datetime.fromtimestamp(tm).strftime('%Y-%m-%d %H:%M:%S')
    
    def _LUT_namedtuple_factory(self, cursor, row):
        return LUT(*row)

#     def _Config_namedtuple_factory(self, cursor, row):
#         """Returns row as a  Config:  """
#         return Config(*row)


    def _create_cols_vals(self, msg):
        '''Filters out fields not in BMS schema,
         Returns two synchronized lists with column names (cols) and values (vals) to facilitate inserts into db.
         BMS_FIELDS in database_interface_config.py must be kept current!!!'''
        cols=[]
        vals=[]
        if "ID" in msg:
            msg.pop("ID")
        rejects=[]
        for k,v in msg.items():
            if k in BMS_FIELDS:
                cols.append(k)
                vals.append(v)
            else:
                rejects.append(k)
        print(" create cols_vals rejected columns: ", rejects)
        return (cols, vals)

#     def list_all_choices(self):
#         """tuple_factory is the function that specifies the namedtuple to use in creating objects from *row
#         For now it is: _Abbrev_namedtuple_factory"""
#         cu = self.get_cursor()
#         #self.cx.row_factory = self._Abbrev_namedtuple_factory
#         select_str = "SELECT id, owner, app_desc, channel_id, channel_desc, version_desc  FROM CONFIG order by owner and channel_id;"
#         records = []
#         for row in cu.execute(select_str):
#             records.append(row)
#         # print("records: ", records)
#         return records

    def next_msgid(self):
        '''Inserts a new msgid and returns the lastrowid which is it.'''
        cu=self.get_cursor()
        cu.execute("INSERT INTO MSGID VALUES(NULL, ?)", (time.time(),) )
        msgid = cu.lastrowid
        return msgid
 
    def get_app_config(self):
        '''For each app, there will be exactly one app_config record'''
        cu =self.get_cursor()
        select_str = f"SELECT * FROM Apps where  version = {self.version};"
        #print("select_str: ", select_str)
        # Each row is a channel.
        res = cu.execute(select_str)
        return res.fetchone()
    
    def get_chan_config(self, chan):
        """tuple_factory is the function that specifies the namedtuple to use in creating objects from *row. Json sends records better than tuples
        """
        cfg = []
        cu =self.get_cursor()
        select_str = f"SELECT * FROM CHANNELS where  app_id = {self.app_id}  and version = {self.version} and chan={chan};"
        #print("select_str: ", select_str)
        # Each row is a channel.
        for row in cu.execute(select_str):
            #print("row: ", row)
            cfg.append(CHAN_CONFIG(*row))
        self.cfgs[chan]=cfg
        return cfg
     #TODO 7: fix get_estimator_parms so that it does not return an odict but the tuple, fix svr_task_mgr, gui also...
    def get_estimator_parms(self ):
        #od_vd_fracts = OrderedDict()
        est_parms=[]
        select_str = f" select chan, slope, intercept from CHANNELS where app_id= {self.app_id} and version = {self.version}"
        #print(" select string: ",  select_str)
        cu = self.get_cursor()
        for row in cu.execute(select_str):
            #print("row: ", row)
            est_parms.append(row)
            #od_vd_fracts[row[0]] =row[1]
      #  return od_vd_fracts
        return est_parms


    #TODO 3 : Implement save_config(...) 
    def save_config(self,  msg:Config):
        '''TBD... used to persist with new values... version update '''
        pass

    def save_to_bms(self , msg):
        ''' Saves summary fields for both types ['m','c'] to the same database table, bms.Summary fields are :
 (ID | MSGID | VERSION | TIMESTAMP | TYPE | CHAN | A2D_MEAN | VM_MEAN |  VM_SD  |  VB  | VIN  |  ERROR  | SAMP_SZ | DISCARD_SZ | KEEP_SZ ).
 Also Saves the A2D samples embedded in msg to the A2D table with the bms_id to link the two tables.A2D Fields are: ( ID | BMS_ID | A2D). where samples is a string
holding list(64 int sample values). This can be expanded in length to have 128 samples etc.
arg msg is a dict loaded by ADC  with raw data and augmented by Server with  computations.
 json is used to convert from string dict. Returns bms_id '''
        print(f"...Entered function: save_to_bms(msg) msg_type: {type(msg)} msg: {msg} ")
        atype = msg["TYPE"]
        a2d = msg["A2D"]
        timestamp = msg['TIMESTAMP']  # this is from the ADC timestamp.
        chan = msg["CHAN"]
        vin = msg["VIN"]
        # filters out msg fields not in BMS. Also remove "ID" so that db puts in next ID.
        cols, vals = self._create_cols_vals(msg)      
         
        print(f"called dbi. save_measurement() with cols: {cols[1:]} values: {vals[1:]} ")
        bms_insert_str = f"insert into BMS {tuple(cols)} values {tuple(vals)}; "   
        cu = self.get_cursor()
        cu.execute(bms_insert_str)
        bms_id=cu.lastrowid
        #print(f"bms_id: {bms_id}")
        a2d_insert_str = f"insert into A2D values(NULL, {bms_id}, '{a2d}')"
        #print(f"a2d_insert_str: {a2d_insert_str}")
        cu.execute(a2d_insert_str)
        self.cx.commit()
        return bms_id

    def list_bms(self, chan, atype):
        ''' Returns a list<records> of type atype.'''
        records = []
        select_str = f" select * from BMS where chan={chan} and type = '{atype}' ;  "
        #print(f"select _str: {select_str}")

        
       # self.cx.row_factory = self._BMS_namedtuple_factory
        cu = self.get_cursor()
        for row in cu.execute(select_str):
            records.append(row)
        return records
    

    def get_bms_a2d_samples(self, bms_id):
        ''' retrieves the a2d samples as a list from tableA2D in order to analyze sample problems'''
        records=[]
        cu = self.get_cursor()
        select_str = f"select samples from A2D where bms_id = {bms_id};"
        #print("select_str: ", select_str)
        for row in cu.execute(select_str):
            records.append(row)
        lst=list(records[0])
        a2d=json.loads(lst[0])
        return a2d
 
    def get_lut_pair(self, chan, vm):  
        cu = self.get_cursor()
        select_str = f"select * from luts where chan = {chan} and version= {self.version} and vm={vm};"
        # print("select_str: ", select_str)
        res = cu.execute(select_str)
        return res.fetchone()
    
    def get_cursor(self):
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        return cu
    
    #TODO 6: Get get_schema working so that dbi can query for the schema of <table> in order to check correctness of namedtuples
    def get_schema(self, table_name):
        '''Returns the schema of 'table_name' '''
        select_str = f".schema {table_name} "
        print(f"sqlite3 {self.db_path} .schema {table_name}")
        
        
      
        
    def get_lut_item(self, chan, vin):
        '''Returns the whole LUT record including ID, given chan and vin.'''
        cu=self.get_cursor()
        select_str= f" select * from LUTS where app_id={self.app_id} and version = {self.version} and chan={chan} and vin={vin}"
        res=cu.execute(select_str)
        return res.fetchone()
    
    def get_lut(self, chan):
        records=[]
        #self.cx.row_factory = self._LUT_namedtuple_factory
        cu = self.get_cursor()
        select_str = f"select id,vm,vin from luts where chan = {chan} and version= {self.version};"
        #print("select_str: ", select_str)
        for row in cu.execute(select_str):
            records.append(row)
        return self.lut_as_od(chan, records)

    def get_lut_timestamp(self,  chan ):
        timestamp = ""
        cu = self.get_cursor()
        select_str = f"select LUT_TS from CONFIG where chan={chan} and version={self.version}";
        res= cu.execute(select_str)
        timestamp = res.fetchone()[0]
        #print(timestamp)
        return timestamp
    
    def update_lut_timestamp(self, chan):
        '''Called when any lut is updated. It updates the lut_timestamp in the config table. dbi instance variables: app_id, version'''
        cu = self.get_cursor()
        timestamp = self._timestamp()    # dbi timestamp is NOW.
        update_str = f"update CHANNELS set LUT_TS ='{timestamp}'  where chan={chan} and version = {self.version}";
        #print(f"update_str: {update_str}")
        cu.execute(update_str)
        self.cx.commit()
           
    def update_lut_pair(self,  lut_item ):
        '''Updates any of: vm, vin value for a given id . The cols for api_id , version are dbi instance variables... '''
        ts = self._timestamp()
        print(f" lut_item.ID : {lut_item.ID}")
        cu = self.get_cursor()
        print(f"chan: {lut_item.CHAN}")
        print(f"pair values to be updated: vm: {lut_item.VM} and vin: {lut_item.VIN}")
        #cfg_update_str = f" UPDATE Config  set LUT_TS ='{ts}' where id = {lut_item.ID};"
        lut_update_str = f" Update LUTS set vm={lut_item.VM} , vin={lut_item.VIN} where id={lut_item.ID} "
        #print("cfg_update_str: ", cfg_update_str)
        cu.execute(lut_update_str)
        #cu.execute(cfg_update_str)
        self.update_lut_timestamp(lut_item.CHAN)
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
        #print(f" od: {od}")
        self.luts[chan]=od
        return od
 
 
    def matchesboundary(self, chan:int, vm:float, version:int) :
        '''Returns tuple(vm, lut). Vm is None if outside of allowed boundary limits, Returns vm if vm is within tol of first or last key. tol is 1/2* vinstep * vd_fract'''
     
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

    def check_bms_id_in_a2d(self):
        '''Returns the id of the last bms record and the bms_id of the last A2D record. Good to ensure sync.'''
        a2d_select_str='select max(bms_id)  from A2D'
        bms_select_str = 'select max(id) from BMS'
        cu = self.get_cursor()
        #print(f"a2d_select_str: {a2d_select_str}")
        #print(f"bms_select_str: {bms_select_str}")
        res=cu.execute(a2d_select_str)
        bms_id = res.fetchone()[0]
        res=cu.execute(bms_select_str)
        _id = res.fetchone()[0]
        #print(f"Returning bms.id = {_id} and a2d.bms_id = {bms_id}")
        return (_id, bms_id) 
        
        

        
