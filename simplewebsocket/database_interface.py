# file: database_interface.py. path: .../DEV/.../data
"""This class will retrieve and store in formation for the DataController which supplies info to the GUIs.
Transactions are used when writing to the db. Each fetch method will include the tuple_factory to be
used to convert the row values to a namedtuple: one of: [_Abbrev_namedtuple_factory, _Config_namedtuple_factory, _BMS_namedtuple_factory,_LUT_namedtuple_factory
"""
import sqlite3
import time
import json
from database_interface_config import db_path, Config, Abbrev, BMS, LUT_INFO
from collections import OrderedDict

class DatabaseInterface:
    def __init__(self, cfg_ids):
        self.db_path = db_path
        self.cfg_ids = cfg_ids
        print(f"dbpath: {self.db_path} ")
        print(f"cfg_ids: {self.cfg_ids} ")

    def build_response(self, message):
        msg= f"Called dbi.build_response() with message: {message}"
        print(f"msg.type:  {type(msg)}  msg:{msg}")
        if message == '350':
            #print("calling dbi.load_config(cfg_ids)")
            astring = self.load_config(self.cfg_ids )
#             astring[0] = astring[0][7:]
#             astring[-1] = astring[-1][:-1]
            response = f"{message} : {astring}"
            print(f"from db load config: {astring} of length: {len(astring)}")
            return json.dumps(response)
        else:
            return(f" {msg} TBD  DB: Work in progress...")
    
    def _timestamp(self):
        """Returns local time as string, eg: YYYY-mm-DD HH:MM:SS"""
        dt = time.localtime()
        return f"{dt[0]}-{dt[1]}-{dt[2]}_{dt[3]}:{dt[4]}:{dt[5]}"  # YYYY-MM-DD  HH:mm:sec (dt[6] dow , dt[7] julian)

    def _Abbrev_namedtuple_factory(self, cursor, row):
        """Returns row as a Abbrev_Record:
        Abbrev = namedtuple("Abbrev",("id", "owner", "app_desc", "version_desc", "channel_id", "channel_desc"))
        """
        return Abbrev(*row)

    def _BMS_namedtuple_factory(self, cursor, row):
        return BMS(*row)

    def _LUT_namedtuple_factory(self, cursor, row):
        return LUT_INFO(*row)

    def _Config_namedtuple_factory(self, cursor, row):
        """Returns row as a  Config:  """
        return Config(*row)
    
    def _create_cols_vals(self, msg):
        '''Removes purpose, Returns two lists with column names (cols) and values (vals).'''
        # db table BMS has no column 'purpose' . ' type'  is used to reflect measurment/calibration instead. remove 'purpose' by pop
        msg.pop('purpose')
        msg.pop("sender_id")
        msg.pop("msg_id")
        cols=[]
        vals=[]
        for k,v in msg.items():
            cols.append(k)
            vals.append(v)
        return (cols, vals)

    def list_all_choices(self):
        """tuple_factory is the function that specifies the namedtuple to use in creating objects from *row
        For now it is: _Abbrev_namedtuple_factory"""
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        self.cx.row_factory = self._Abbrev_namedtuple_factory
        select_str = "SELECT id, owner, app_desc, channel_id, channel_desc, version_desc  FROM CONFIG order by owner and channel_id;"
        records = []
        for row in cu.execute(select_str):
            records.append(row)
        # print("records: ", records)
        return records

    
    def load_config(self, ids):
        """tuple_factory is the function that specifies the namedtuple to use in creating objects from *row
        For this select, it is one of: [_Abbrev_namedtuple_factory, _Config_namedtuple_factory,BMS]...TBD
        """
        cfg = []
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        self.cx.row_factory = self._Config_namedtuple_factory
        cu = self.cx.cursor()
        select_str = f"SELECT * FROM CONFIG where  id in {(ids)} ORDER BY CHAN;"
        print("select_str: ", select_str)
        # Each row is a channel.
        for row in cu.execute(select_str):
            #print("row: ", row)
            cfg.append(row)
        return cfg

    #TODO 3 : Implement save_config(...) 
    def save_config(self, cfg_id:int, msg:Config):
        '''TBD... handles next version'''
        pass

    def _format_insert(self, insert_str):
        """quotes the keep list."""
        insert_str = insert_str.replace("[", "'[")
        insert_str = insert_str.replace("]", "]'")
        return insert_str

    def save_measurement(self, msg):
        """Use the values in msg to populate values in insert statement."""
        # msg is a dict for Battery Management System (bms) . it is from the client
        # print("Called dbi.save_measurement(). Saving msg to database...", bms)
        # create correct insert_str:  stringify keep, end with semicolon, ;.
        print(f" save_measurement(...) li 109 type (msg): {type(msg)}  msg: {msg} ")
        msg["type"] = "m"
        ts = self._timestamp()
        msg["timestamp"] = ts
        cols, vals = self._create_cols_vals(msg)
        print(f"called dbi. save_measurement() with cols: {cols} values: {vals} ")
        insert_str = f"insert into BMS {tuple(cols)} values {tuple(vals)}; "
        insert_str = self._format_insert(insert_str)
        print(f" insert_str: {insert_str}")
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        cu.execute(insert_str)
        self.cx.commit()

    def save_calibration(self, msg):
        """saves all in the BMS table. the type column will show 'c'"""
        msg["type"] = "c"
        ts = self._timestamp()
        msg["timestamp"] = ts
        cols, vals = self._create_cols_vals(msg)
        print(f" cols: {cols} vals: {vals}")
        insert_str = f"insert into BMS {tuple(cols)} values {tuple(vals)}  "
        print(f" insert str: {insert_str}")
        insert_str = self._format_insert(insert_str)
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        cu.execute(insert_str)
        self.cx.commit()

    def list_measurements(self, chan):
        ''' Returns a list<records>. cfg_id is one of cfg_ids '''
        records = []
        cfg_id = self.cfg_ids[chan]
        select_str = " Select * from BMS where type = 'm' and cfg_id = cfg_id "
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        self.cx.row_factory = self._BMS_namedtuple_factory
        cu = self.cx.cursor()
        for row in cu.execute(select_str):
            records.append(row)
        return records
    
    def list_calibrations(self):
        records = []
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        self.cx.row_factory = self._BMS_namedtuple_factory
        cu = self.cx.cursor()
        #select_str = "SELECT  id, cfg_id ,type ,chan , timestamp , sample_sz ,  a2d , a2d_sd , vm , vb , vin , error ,  sample_period , store_time , gate_time, keep  from BMS where type = 'c' ;"
        select_str = "SELECT * from BMS where type = 'c' ;"
        #print("select_str: ", select_str)
        # Each row is a record.
        for row in cu.execute(select_str):
            # print("row: ", row)
            records.append(row)
        return records
     
    def get_lut(self, chan):
        records=[]
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        self.cx.row_factory = self._LUT_namedtuple_factory
        cu = self.cx.cursor()
        select_str = f"SELECT LUT, LUT_TS FROM CONFIG where  chan = {chan};"
        print("select_str: ", select_str)
        for row in cu.execute(select_str):
            records.append(row)
        return records
         
     #TODO 2: Implement and Test update_lut(...)
    #TODO 4: Add lut_timestamp to Config table, so a new LUT will be datetimestamped without changing the config timestamp.
    def update_lut(self, msg):
        '''TBD... msg will hold lut,  id'''
        chan=msg["chan"]
        lut = str(msg["LUT"])
        ts = self._timestamp()
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        update_str = f" UPDATE Config  set lut_ts ='{ts}', LUT='{lut }' where chan ={chan} ;"
        print("update_str: ", update_str)
        cu.execute(update_str)
        self.cx.commit()
    