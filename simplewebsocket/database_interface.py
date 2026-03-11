# file: database_interface.py. path: .../DEV/.../data
"""This class will retrieve and store in formation for the DataController which supplies info to the GUIs.
Transactions are used when writing to the db. Each fetch method will include the tuple_factory to be
used to convert the row values to a namedtuple: one of: [_Abbrev_namedtuple_factory, _Config_namedtuple_factory, _BMS_namedtuple_factory,_LUT_namedtuple_factory
Later it was determined to send raw tuples across the websocket and to apply the namedtuples in the client requesting the data
"""
import sqlite3
import time
import json
from database_interface_config import db_path, Config, Abbrev, BMS, LUT,CONFIG_FIELDS, BMS_FIELDS
from collections import OrderedDict
import re
import math

class DatabaseInterface:

    def __init__(self,app_id):
        self.db_path = db_path
        self.app_id =app_id
        print(f"dbpath: {self.db_path} ")
        print(f"app_id: {self.app_id} ")
        self.luts: [OrderedDict, OrderedDict, OrderedDict] =[{},{},{}]
        self.lut_timestamps:[str, str, str] = ["","",""]
        cmds= dict()
        cmds['150']=self. list_measurements( 0)
        cmds['152']=self. list_measurements( 1)
        cmds['154']=self. list_measurements( 2)
        cmds['310']=self.load_config(self.app_id )
        cmds['360']=self.luts[0]=self.lut_as_od(0, self.get_lut( 0))
        cmds['362']=self.luts[1]=self.lut_as_od(1, self.get_lut( 1))
        cmds['364']=self.luts[2]=self.lut_as_od(2, self.get_lut( 2))
        cmds['370']=self.lut_timestamps[0]= self.get_lut_timestamp(0)
        cmds['372']=self.lut_timestamps[1]= self.get_lut_timestamp(1)
        cmds['374']=self.lut_timestamps[2]= self.get_lut_timestamp(2)
        self.cmds=cmds
    

    def build_response(self, message):
        msg= f"Called dbi.build_response() with message: {message}"
        #print(f"msg.type:  {type(msg)}  msg:{msg}")
        response = f" {msg} TBD  DB: Work in progress..."
        # lookup in dict cmds to see what method to call:
        return_purpose=int(message) +1
        astring= self.cmds[message]
        response = f" request purpose: {message} response purpose: {return_purpose} , {astring}"
        print(response)
        return json.dumps(response)
    
    def _timestamp(self):
        """Returns local time as string, eg: YYYY-mm-DD HH:MM:SS"""
        dt = time.localtime()
        return f"{dt[0]}-{dt[1]}-{dt[2]}_{dt[3]}:{dt[4]}:{dt[5]}"  # YYYY-MM-DD  HH:mm:sec (dt[6] dow , dt[7] julian)

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
        #self.cx.row_factory = self._Abbrev_namedtuple_factory
        select_str = "SELECT id, owner, app_desc, channel_id, channel_desc, version_desc  FROM CONFIG order by owner and channel_id;"
        records = []
        for row in cu.execute(select_str):
            records.append(row)
        # print("records: ", records)
        return records

    
    def load_config(self, aid):
        """tuple_factory is the function that specifies the namedtuple to use in creating objects from *row
        For this select, it is one of: [_Abbrev_namedtuple_factory, _Config_namedtuple_factory,BMS]...TBD
        """
        cfg = []
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        #self.cx.row_factory = self._Config_namedtuple_factory
        cu = self.cx.cursor()
        select_str = f"SELECT * FROM CONFIG where  app_id = {aid} ORDER BY CHAN;"
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
        ''' Returns a list<records>.'''
        records = []
        select_str = f" Select * from BMS where type = 'm' and chan = {chan} "
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
       # self.cx.row_factory = self._BMS_namedtuple_factory
        cu = self.cx.cursor()
        for row in cu.execute(select_str):
            records.append(row)
        return records
    
    def list_calibrations(self):
        records = []
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
       # self.cx.row_factory = self._BMS_namedtuple_factory
        cu = self.cx.cursor()
        select_str = "SELECT * from BMS where type = 'c' ;"
        #print("select_str: ", select_str)
        # Each row is a record.
        for row in cu.execute(select_str):
            # print("row: ", row)
            records.append(row)
        return records

    def store_samples(self, bms_id:int, a2d_samples:list[int]):
        '''stores a2d_samples into Samples Table, keyed by the bms_id'''
        samps = json.dumps(a2d_samples)
        insert_str = f"insert into SAMPLES values (NULL, bms_id = {bms_id}, a2d ={samps});"
        print("insert_str: ", insert_str)
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        cu.execute(insert_str)
        self.cx.commit()
    
    def stats(self, chan:int, samples:list[int]):
        ''' Compures m,sd,vm,vb, from  samples'''
        print(f"type(samples): {type(samples)} ")
        m=int(round(sum(samples)/len(samples),3))
        vars = [(x-m)*(x-m) for x in samples]
        lsb=4.095/32768
        sd = round(math.sqrt(sum(vars)/len(vars))*lsb,6)
        vm=round(lsb*m,3)
        vb = round(self.lookup_chan_vm(chan, vm),3)
        print(" a2d_mean, vm_mean, vm_sd, vb estimate")
        return m, vm , sd, vb
        
    def get_samples(self, bms_id):
        ''' retrieves the a2d samples as a list from table SAMPLES and computes m, sd...'''
        records=[]
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        #self.cx.row_factory = self._LUT_namedtuple_factory
        cu = self.cx.cursor()
        select_str = f"select a2d from samples where bms_id = {bms_id};"
        print("select_str: ", select_str)
        for row in cu.execute(select_str):
            records.append(row)
        lst=list(records[0])
        a2d=json.loads(lst[0])
        return a2d
     
    def get_lut(self, chan):
        records=[]
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        self.cx.row_factory = self._LUT_namedtuple_factory
        cu = self.cx.cursor()
        select_str = f"select vm,vin from luts where channel = {chan};"
        print("select_str: ", select_str)
        for row in cu.execute(select_str):
            records.append(row)
        return records

    def get_lut_timestamp(self, chan):
        timestamp = ""
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        select_str = f"select LUT_TS from CONFIG where chan={chan}";
        res= cu.execute(select_str)
        timestamp = res.fetchone()[0]
        print(timestamp)
        return timestamp
    
     #TODO 2: Implement and Test update_lut(...)
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
    
    #TODO 5: Copy lut_as_od to the gui_client.py module if cannot send od across the wire.
    def lut_as_od(self, chan, lut):
        '''lut is any of lut0, lut1, lut2 and is a list of str. This method uses re to findall stings which are decimal numbers.
        Method takes in list returned by db, converts it into an OrderedDict... and stores it in luts[chan]'''
        vm=[]
        vin=[]
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

    #TODO 6: Copy lookup_chan_vm()  to the gui_client.py module, depending on who does get_samples and stats(), the lookup of vb using vm
    def lookup_chan_vm(self,  chan, vm):
        '''Given any legitimate value for vm (measured voltage) in a channel, chan,  return the estimate of vb (battery voltage), using interpolation.
           First  if vm is == to a boundary returns lut[vm], then if  out of bounds returns error statement, else interpolates vm to yield vb '''
        lut=self.luts[chan]
        minkey=10
        maxkey=-10
        minval=15
        maxval=-15
        for k,v in lut.items():
            minkey=min(minkey, k)
            maxkey=max(maxkey,k)
            minval= min(minval,v)
            maxval=max(maxval,v)
        print( f"\t bounds for chan { chan} : {minkey} , {maxkey} maps to: {minval} , {maxval}")
        # if vm is on a boundary , return lut(vm)
        if vm==minkey or vm==maxkey:
            return lut[vm]
        #    out of bounds returns error statement
        elif vm < minkey or vm >= maxkey:
            return f" \t Error: vm is out of bounds. violates: {minkey} <=  vm: {vm}  < {maxkey}. "
        else:
            #  if inside boundaries, find keys that bracket vm
            print(f"\tvm is in range.: {minkey}  <  {vm}  <  {maxkey} ... OK")
            vhi=-1
            vlo=10
            for k,v in lut.items():
                if vm < k:
                    vhi=k
                    break    # important! w/o break vhi will run all the way to highest vm in od.
                else:
                    vlo=k
            # then interpolate using vlo,vhi, vm
            print(f"\tvlo: {vlo} vm: {vm}  vhi: {vhi}")
            rvm = vhi - vlo
            fract=(vm-vlo)/rvm
            vbhi=lut[vhi]
            vblo=lut[vlo]
            vb = round(vblo + fract * (vbhi-vblo), 3)
            # print(f"interpolated value for {vm} is {vb}")
            return vb        
        
        