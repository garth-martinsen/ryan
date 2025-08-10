#file: database_interface.py
''' This class will retrieve and store information for the DataController which supplies info to the GUIs.
Transactions are used when writing to the db. Each fetch method will include the tuple_factory to be
used to convert the row values to a namedtuple: one of: [_short_namedtuple_factory, _config_namedtuple_factory]'''
import sqlite3
import time
#import json
from database_interface_config import  db_path, Config,  Short_Record
from database_interface_config import CFG_Columns,   BMS_Columns
from database_interface_config import  BMS

class DatabaseInterface:
    def __init__(self):
        self.db_path = db_path

    def timestamp(self):
        '''Returns local time as string, eg: YYYY-mm-DD HH:MM:SS'''
        dt = time.localtime()
        return f'{dt[0]}-{dt[1]}-{dt[2]}  {dt[3]}:{dt[4]}:{dt[5]}'  # YYYY-MM-DD  HH:mm:sec (dt[6] dow , dt[7] julian)
    

    def list_calibrations(self):
        calibs=[]
        self.cx =  sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        self.cx.row_factory=self._config_namedtuple_factory
        cu = self.cx.cursor()
        select_str="SELECT  id, type, timestamp, vin, vm, vb, error from BMS;"
        print("select_str: ", select_str)
        #Each row is a channel.
        for row in cu.execute(select_str) :
            #print("row: ", row)
            calibs.append(row)
        return calibs

    def _short_namedtuple_factory(self, cursor, row):
        ''' Returns row as a Short_Record:
           Short_Record = namedtuple("Short_Record",("id", "owner", "app_desc", "version_desc", "channel_id", "channel_desc"))
        '''
        return Short_Record(*row)
   
    def bms_namedtuple_factory(self, cursor,row):
       return BMS(*row)
        
        
    def _config_namedtuple_factory(self, cursor, row):
        ''' Returns row as a  Config:
           Config = namedtuple("Config", ("id", "owner", "app_id", "app_desc", "channel_id", "channel_description",
                                                                "version_id","version_description", "creation_time","mosfet",
                                                                "mosfet_type" ,"tempC", "r1","r2","rp","rg","LUT_CALIBRATED", "LUT") )
       '''
        return Config(*row)
 
    def list_all_choices(self):
        '''tuple_factory is the function that specifies the namedtuple to use in creating objects from *row
          For now it is: _short_namedtuple_factory'''
        self.cx =  sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        self.cx.row_factory=self._short_namedtuple_factory
        select_str = 'SELECT id, owner, app_desc, channel_id, channel_desc, version_desc  FROM CONFIG order by owner and channel_id;'
        records = []
        for row in cu.execute(select_str) :
            records.append(row)
        #print("records: ", records)
        return records
        
    def load_config(self, ids):
        '''tuple_factory is the function that specifies the namedtuple to use in creating objects from *row
          For this select, it is one of: [_short_namedtuple_factory, _config_namedtuple_factory]'''
        cfg=[]
        self.cx =  sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        self.cx.row_factory=self._config_namedtuple_factory
        cu = self.cx.cursor()
        select_str=f"SELECT * FROM CONFIG where  id in {ids} ORDER BY CHANNEL_ID;"
        print("select_str: ", select_str)
        #Each row is a channel.
        for row in cu.execute(select_str) :
            #print("row: ", row)
            cfg.append(row)
        return cfg
    
    
    def create_next_version_records(self):
        '''Creates  new records which will store a new version of  LUT for each channel. TBD'''
        pass
    
    def save_config(self):
        pass
    
    def format_insert(self, insert_str):
        ''' quotes the keep list. '''
        insert_str = insert_str.replace('[', '\'[')
        insert_str = insert_str.replace(']', ']\'')
        return insert_str
    
    def create_cols_vals(self, msg):
        '''Removes purpose, Returns two lists with column names (cols) and values (vals).'''
        # db table BMS has no column 'purpose' . ' type'  is used to reflect calibration instead. remove 'purpose' by pop
        msg.pop('purpose')
        cols=[]
        vals=[]
        for k,v in msg.items():
            cols.append(k)
            vals.append(v)
        return (cols, vals)
    
    def save_measurement(self, msg):
        ''' Use the values in msg to populate values in insert statement.'''
         # msg is a dict for Battery Management System (bms) . it is from the client
         # print("Called dbi.save_measurement(). Saving msg to database...", bms)
        #TODO:Make sure that transaction is not needed in BMS save.
        # create correct insert_str:  stringify keep, end with semicolon, ;.
        msg['type'] ='m'
        ts=self.timestamp()
        msg["timestamp"]=ts
        cols, vals = self.create_cols_vals(msg)
        print(f"called dbi. save_measurement() with cols: {cols} values: {vals} ")
        insert_str = f"insert into BMS {tuple(cols)} values {tuple(vals)}; "
        insert_str= self.format_insert(insert_str)
        self.cx =  sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        cu.execute(insert_str)

    def save_calibration(self, msg): 
        ''' saves all in the BMS table. the type column will show 'c' '''
        msg['type']='c'
        cols, vals=self.create_cols_vals(msg)
        insert_str = f"insert into BMS {tuple(cols)} values {tuple(vals)}  "
        insert_str= self.format_insert(insert_str)
        self.cx =  sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        cu.execute(insert_str) 

    def list_BMS(self):
        calibs=[]
        select_str=" Select * from BMS where type = 'c' "
        self.cx =  sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        for row in cu.execute(select_str) :
            #print("row: ", row)
            calibs.append(row)
        return calibs
        
#     def store_lut(self, lut_json, channel_id, version_id, version_desc):
#         '''Stores a new record in config table. values are for whole row but some are replaced with new info'''
#         #TODO: Needs testing...
#         columns= tuple(Columns)
#         values=[self.cfg]
#         values[1]=version_id
#         values[2]=version_desc
#         values[4]=channel_id
#         values[5]=int(time.time())
#         values[12]=lut_json
#         values=tuple(values)
#         print(columns, values)    
#         insert_str =f"INSERT INTO CONFIG {Columns}{values}"
#         print("insert_str: ", insert_str)
#         self.cu.execute("begin")
#         self.cu.execute(insert_str)
#         self.cu.execute("commit") 
        #TODO 1: Problem: db is locked when I go to cli to check the results. # TODO 1: Fixed! use transaction . 

    def save_data(self):
        pass
    
  
