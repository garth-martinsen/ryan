#file: database_interface.py. path: .../DEV/.../data

"""This class will retrieve and store information for the SvrTaskManager which supplies info to the GUIs.
Transactions are used when writing to the db. 
It was determined to send raw tuples across the tCP comms and to apply the namedtuples in the client requesting the data
"""
import sqlite3
from svr.database_interface_config import  APP_CONFIG, CHAN_CONFIG, BMS, LUT,APP_CONFIG_FIELDS, CHAN_CONFIG_FIELDS, BMS_FIELDS, AMP_HRS_FIELDS, AMP_HRS, Stats, funct_desc
from common import secrets
from common.bms_config import APP_ID, VERSION
from collections import OrderedDict, namedtuple
import time
import datetime
import json
import re
import math
from typing import List

print(f" from secrets: db_path: {secrets.db_path}")

# ID | APP_ID | VERSION | CHAN |   VM   | VIN  |
LUT_ITEM = namedtuple("LUT_ITEM", ("ID", "APP_ID", "VERSION", "CHAN", "VM", "VIN", ))
 
class DatabaseInterface:

    def __init__(self,APP_ID, VERSION):
        self.db_path = secrets.db_path
        self.app_id =APP_ID
        self.version=VERSION
        print(f"dbpath: {self.db_path} ")
        print(f"app_id: {self.app_id} ")
        print(f"version: {self.version}")
        self.app_cfg: APP_CONFIG()
        self.chan_cfgs: List[CHAN_CONFIG(),CHAN_CONFIG(), CHAN_CONFIG()]= [[],[],[]]
        self.luts :List[OrderedDict] =[OrderedDict(),OrderedDict(),OrderedDict()]
        self.lut_timestamps:List[str] = ["","",""]
        '''│      SLOPE       │     intercept      │
           ├──────────────────┼────────────────────┤
           │ 1.33289430358907 │ 0.024164327787965  │
           │ 2.98747763864043 │ 0.0498818752307106 │
           │ 3.99304865938431 │ 0.0641294273419395 │
           The slope and intercepts should be loaded from dbi... This is a temporary cluge.
        '''
        self.slope=[1.33289430358907,2.98747763864043,3.99304865938431 ]
        self.intercepts= [0.024164327787965,0.0498818752307106,0.0641294273419395 ]
        self.msg = ""
        self.funct_desc = funct_desc

    def get_max_meas_id(self ):
        '''Selects the max(meas_id) from bms table and return it to adc to set its meas_id on startup. '''
        cu = self.get_cursor()
        select_str = f"select max(meas_id) from bms where app_id={self.app_id} and version={self.version}; "
        res = cu.execute(select_str)
        return res.fetchone()[0]
    
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


    def _create_cols_vals(self, msg, table_fields):
        '''Filters out fields not in BMS schema,
         Returns two synchronized lists with column names (cols) and values (vals) to facilitate inserts into db.
         BMS_FIELDS in database_interface_config.py must be kept current!!!'''
        print(f"type and content of msg: {type(msg)} msg: {msg}")
        cols=[]
        vals=[]
        rejects=[]
        for k,v in msg.items():
            if k == "ID":
                continue
            if k in table_fields:
                cols.append(k)
                vals.append(v)
            else:
                rejects.append(k)
        print(" create cols_vals rejected columns: ", rejects)
        print(" cols_vals: ", cols, vals)
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
        '''For each (app,version), there will be exactly one app_config record'''
        cu =self.get_cursor()
        select_str = f"SELECT * FROM Apps where ID = {self.app_id} and version = {self.version};"
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
        res = cu.execute(select_str)
        return res.fetchone()

     #TODO 7: fix get_estimator_parms so that it does not return an odict but the tuple, fix svr_task_mgr, gui also...
    def get_estimator_parms(self, chan ):
        est_parms=[]
        select_str = f" select chan, slope, intercept from CHANNELS where app_id= {self.app_id} and version = {self.version} and chan={chan}"
        #print(" select string: ",  select_str)
        cu = self.get_cursor()
        for row in cu.execute(select_str):
            #print("row: ", row)
            est_parms.append(row)
        return est_parms

    def update_estimator_parms(self, chan, slope, intercept):
        '''Persists new slope and intercept to CHANNELS table.'''
        cu = self.get_cursor()
        update_str = f"update CHANNELS set SLOPE= {slope} and INTERCEPT = {intercept} where CHAN = {chan} "
        cu.execute(update_str)


    #TODO 3 : Implement save_config(...) This should  indicate a new version! 
    def save_config(self,  msg:Config):
        '''TBD... used to persist with new values... version update '''
        pass

    def save_to_bms(self , msg):
        ''' Saves summary fields for both types ['m','c'] to the same database table, bms.Summary fields are :
        Also Saves the A2D samples embedded in msg to the A2D table with the bms_id to link the two tables.
        A2D Fields are: ( ID | BMS_ID | A2D). where samples is a string
        holding list(64 int sample values).In the Future this could be expanded in length to have 128 samples etc.
        arg msg is a dict loaded with raw data by ADC and augmented by Server computations.
        json.loads() is used to convert from string dict. Returns bms_id '''
        
        cu = self.get_cursor()
        print(f"...Entered function: save_to_bms(msg) msg_type: {type(msg)} msg: {msg} ")
        atype = msg["TYPE"]
        timestamp = msg["TIMESTAMP"]  # this is from the ADC timestamp.
        chan = msg["CHAN"]
        vin = msg["VIN"]
        a2d = msg["A2D"]
        msg["APP_ID"]=self.app_id 
        # filter out msg fields not in BMS. Also remove "ID" so that db puts in next ID.
        print("BMS_FIELDS type:", type(BMS_FIELDS))
        print("BMS_FIELDS content:", repr(BMS_FIELDS))
        print("msg keys:", list(msg.keys()))
        cols, vals = self._create_cols_vals(msg, BMS_FIELDS)
        if not cols:
            raise ValueError( f"No message keys matched BMS_FIELDS: {BMS_FIELDS!r}")
        print(f"called dbi.save_to_bms() with cols: {cols[1:]} values: {vals[1:]} ")
        column_names = ", ".join(cols)
        placeholders = ", ".join("?" for _ in vals)
        print(f"\tcolumn_names: {column_names}, placeholders: {placeholders}")
        sql = f"INSERT INTO BMS ({column_names}) VALUES ({placeholders})"
        cu.execute(sql, vals)
        bms_id=cu.lastrowid
        #print(f"bms_id: {bms_id}")
        a2d_insert_str = f"insert into A2D values(NULL, {bms_id}, '{a2d}')"
        #print(f"a2d_insert_str: {a2d_insert_str}")
        cu.execute(a2d_insert_str)
        return bms_id

    def get_ah_total(self):
        '''Returns the most recent ah_total from amp_hrs db table. function 334.'''
        #TODO: find Chat's suggestion to get latest ah_total from amp_hrs table:ORDER BY ID DESC LIMIT 1
        app_id = self.app_id
        version = self.version
        select_str = "select ah_total from AMP_HRS WHERE APP_ID = app_id and VERSION = version ORDER BY ID DESC LIMIT 1; "
        cu = self.get_cursor()
        res = cu.execute(select_str)
        return res.fetchone()[0]
 
    def save_amp_hrs(self, dict):
        '''Gets the latest ah_total from amp_hrs table, then adds ah_used and saves updated tuple to amp_hrs table.
        #AMP_HRS_FIELDS: ID │ APP_ID │ VERSION │ MEAS_ID │    TIMESTAMP     │ I_MEAN │ PERIOD_SEC │ AH_USED │ AH_TOTAL │'''
        prev_ah_total = self.get_ah_total()
        AH_USED = float(dict["AH_USED"])
        dict["AH_TOTAL"] = prev_ah_total + AH_USED
        dict["APP_ID"] = self.app_id
        dict["VERSION"] = self.version
        cols, vals = self._create_cols_vals(dict, AMP_HRS_FIELDS)
        ins_str = f"insert into AMP_HRS  {tuple(cols)} values {tuple(vals)}; "
        print("ins_str: ", ins_str)
        cu = self.get_cursor()
        cu.execute(ins_str)

    def get_amp_hrs_by_meas_id(self, meas_id):
        '''Returns the amp_hrs record with meas_id'''
        version= self.version
        app_id=self.app_id
        select_str = f"select * from AMP_HRS where APP_ID = app_id and VERSION = version and meas_id={meas_id};"
        cu=self.get_cursor()
        res= cu.execute(select_str)
        return AMP_HRS(*res.fetchone())

        '''Selects the last record saved in AMP_HRS table.'''
    def get_last_amp_hrs(self):
        '''Selects the last record saved in AMP_HRS table.'''
        version= self.version
        app_id=self.app_id
        AMP_HRS_ROW = namedtuple("AMP_HRS_ROW", (AMP_HRS_FIELDS))
        select_str = "select * from AMP_HRS where APP_ID = app_id and VERSION = version ORDER BY ID DESC LIMIT 1;"
        cu=self.get_cursor()
        res = cu.execute(select_str)
        return AMP_HRS_ROW(*res.fetchone())

    def delete_test_records(self):
        """Delete test records with MEAS_ID > 9990."""
        cu = self.get_cursor()
        cu.execute(""" DELETE FROM A2D WHERE BMS_ID IN ( SELECT ID FROM BMS WHERE MEAS_ID > 9990) """)
        cu.execute("DELETE FROM BMS WHERE MEAS_ID > 9990")
        cu.execute("DELETE FROM AMP_HRS WHERE MEAS_ID > 9990")
        cu.connection.commit()

    def list_bms(self, chan, atype):
        ''' Returns a list<records> of type atype.'''
        records = []
        select_str = f" select * from BMS where APP_ID={self.app_id} and VERSION = {self.version} and chan={chan} and type = '{atype}' ;  "
        #print(f"select _str: {select_str}")
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
        res = cu.execute(select_str)
        return res.fetchone()
 
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
 
    def check_bms_id_in_a2d(self):
        '''Returns the id of the last bms record and the bms_id of the last A2D record. Good to ensure sync.'''
        a2d_select_str='select max(id),bms_id  from A2D'
        bms_select_str = 'select max(id) from BMS'
        cu = self.get_cursor()
        #print(f"a2d_select_str: {a2d_select_str}")
        #print(f"bms_select_str: {bms_select_str}")
        res=cu.execute(a2d_select_str)
        bms_id = res.fetchone()[1]
        res=cu.execute(bms_select_str)
        _id = res.fetchone()[0]
        print(f"Returning bms.id = {_id} and a2d.bms_id = {bms_id}")
        return (_id, bms_id) 
        
        
    def save_GPS(self, timestamp, latitude, longitude, altitude_m, hdop):
        '''Saves GPS record to GPS table.'''
        cu = self.get_cursor()
        insrt_str = f"INSERT INTO GPS values (NULL, {timestamp},{latitude}, {longitute}, {altitude_m}, {hdop});"
        cu.execute(insrt_str)
         
    def get_GPS(self, timestamp1, timestamp2):
        '''Returns all GPS Records between two timestamps'''
        records = []
        cu = self.get_cursor()
        select_str = f"SELECT * FROM GPS WHERE TIMESTAMP BETWEEN timestamp1 and timestamp2; "
        for row in cu.execute(select_str):
            records.append(row)
        return records
 
    def get_measurement_report_for_chan(self, meas_id, ch):
        '''Retrieve the bms record for channel ch.'''
        select_str = f"select * from bms where APP_ID= {self.app_id} and VERSION= {self.version} and meas_id = {meas_id} and chan = {ch}"
        cu = self.get_cursor()
        res=cu.execute(select_str)
        return res.fetchone() 
