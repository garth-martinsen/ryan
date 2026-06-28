# file test_dbi.py  Given a msg, save the bms in the msg to BMS table in database rt_db.   Run in Python3

from database_interface import DatabaseInterface, LUT_ITEM
from database_interface_config import Config, LUT, BMS, BMS_FIELDS, CONFIG_FIELDS
from dbi_records import  configs,  bms, samples, answers, lut_answers
#from lut_convert import LutConvert as LC
from collections import OrderedDict
from copy import deepcopy
import json

app_id=1
version=3
# samps = '[21357, 21354, 21351, 21353, 21355, 21357, 21351, 21357, 21351, 21355, 21357, 21353, 21356, 21358, 21356, 21358, 21357, 21355, \
# 21353, 21355, 21355, 21355, 21355, 21356, 21351, 21358, 21356, 21358, 21358, 21353, 21352, 21358, 21358, 21353, 21355, 21357, 21356, \
# 21353, 21354, 21356, 21358, 21356, 21355, 21358, 21351, 21351, 21354, 21356, 21351, 21352, 21354, 21355, 21355, 21352, 21354, 21358, \
# 21355, 21356, 21358, 21357, 21356, 21357, 21352, 21353]'
print("Database initialization: =======================")        

dbi = DatabaseInterface(app_id,version)
print("End of Database initialization: =======================")        

#6/6/26: BMS_FIELDS = ("ID", "MSGID", "VERSION", "TIMESTAMP", "TYPE", "CHAN", "A2D_MEAN", "VM_MEAN", "VM_SD", "VB", "VIN", "ERROR", "SAMP_SZ", "DISCARD_SZ", "KEEP_SZ", "SAMPLES")

# missing until computed: "A2D_MEAN", "VM_MEAN", "VM_SD", "VB", "ERROR"
start_msg=  {'PURPOSE':101, 'MSGID': 5010, "VERSION": 3, 'TIMESTAMP': '2026-2-23  15:31:21.54',  'TYPE': 'm', 'CHAN': 1,
                       "A2D_MEAN": 21355.0, "VM_MEAN": 2.669375 , "VM_SD" : 0.00028038, "VB": 7.9747, "ERROR": 0.02529, "VIN": 7.97,
                       "SAMP_SZ": 64,"DISCARD_SZ": 2, "KEEP_SZ": 62,
               "A2D":  '[21357, 21354, 21351, 21353, 21355, 21357, 21351, 21357, 21351, 21355, 21357, 21353, 21356, 21358, \
                21356, 21358, 21357, 21355, 21353, 21355, 21355, 21355, 21355, 21356, 21351, 21358, 21356, 21358, 21358, 21353, 21352, 21358, \
                21358, 21353, 21355, 21357, 21356, 21353, 21354, 21356, 21358, 21356, 21355, 21358, 21351, 21351, 21354, 21356, 21351, 21352, \
                21354, 21355, 21355, 21352, 21354, 21358, 21355, 21356, 21358, 21357, 21356, 21357, 21352, 21353] ' }


class Test_DBI:
    def __init(self, version):
        self.version = version
        print(f" app_id: {dbi.app_id}  version: {dbi.version}")
        self.cfgs=[Config(),Config(),Config()]

    def test_cols_vals(self, msg):
        print("===================")
        print("testing create_cols_vals()")
        ts= dbi._timestamp()
        msg['timestamp']=ts
        msg["sender_id"]="adc_client"
        msg["msg_id"]=1234
        msg["chan"]=0
        cols, vals = dbi._create_cols_vals(msg)
        #print(f" cols: {cols}  vals: {vals}")
        assert len(cols) == len(vals), "Cols and Vals must have same length"
        print("Passed  test_cols_vals")
     
    #for the given channel 0. Testing is done on 1st and  last pairs....'''
    '''Selects the lut for the channel 0. '''
    def test_get_lut(self, chan):
        #print("===================")
        print(f"testing get_lut({chan})")
        lut= dbi.get_lut(chan)
        lut=OrderedDict(lut)
        first_vm=min(lut.keys())
        last_vm = max(lut.keys())
        print(f"lut: {lut}")
        print(f"type of lut:  { type(lut)} , lut: { lut} ")
        firstvin=lut[first_vm]
        lastvin = lut[last_vm]
        assert firstvin == lut_answers[chan][0]  , f" firstvin {firstvin } is wrong ; it should be first value in lut : {lut_answers[chan][0]} "
        assert lastvin == lut_answers[chan][1] ,   f" lastvin is wrong ; it should be  last value in lut : {lut_answers[chan][1]} "
         
        print(f"Passed  test_get_lut chan: {chan}")
         
     #TODO 6: This test queries the db. Not good practice for unit tests... Also too many literals...  
    def test_load_config(self, app_id, chan):
        '''fetches the  record from the CONFIG table for the chan'''
        print("===================")
        print(f"testing load_config() for chan: {chan}")
        # get config from the databaseInterface on table config.
        record = dbi.get_config( chan)
        print(f"type(record):  {type(record)} config record for chan :{chan}: {Config(*record[0])} ")
        cfg= Config(*record[0])
        #dbi.cfgs[chan]=cfg
       # print(f" config[0]: {configs[chan]}")
        #assert len(records) == 3, "There should be only 3 records, one for each channel"
       
        EPS=1e-6
        if chan == 0:
            print(f"R1 {cfg.R1}  R2: {cfg.R2}")
            assert cfg.CHAN_DESC ==  'One Cell 3.0-4.5V' , "Wrong description"
            assert abs(cfg.R1  -    101100) < EPS, f"Wrong value for R1. Should be: {configs[0].R1}"
            assert abs(cfg.R2  -  303700) < EPS, f"Wrong value for r2. Should be: {configs[0].R2}"
            assert cfg.C1 - 1.0e-07 < EPS, f"Wrong value for C1. Should be {1e-07}"

        elif chan == 1:
            print(f"chan 1 R1: {cfg.R1}  R2: {cfg.R2}")
            assert cfg.CHAN_DESC == 'Two Cells 6.0-9.0V' , "Wrong description"
            assert (cfg.C1 - 1.0e-07 < EPS), f"Wrong value for C1. Should be {1e-07}"
            assert (cfg.R1 - 222200 < EPS) , f"Wrong value for r1. Should be: {cfg.R1}"
            assert (cfg.R2 - 111800 <EPS) , f"Wrong value for r2. Should be: {cfg.R2}"
            assert (cfg.C1 - 1.0e-07 < EPS), f"Wrong value for C1. Should be {1e-07}"

        elif chan == 2:
            print(f" chan 2 R1: {cfg.R1}  R2: {cfg.R2}")
            assert cfg.CHAN_DESC == 'Three Cells 9.0-13.5V', "Wrong description"
            assert cfg.R1== 301400,f"Wrong value for R1. Should be: {cfg.R1}"
            assert cfg.R2 == 100700,  f"Wrong value for R2. Should be: {cfg.R2}"
            assert cfg.C1 - 1.0e-07 < EPS, f"Wrong value for C1. Should be {1e-07}"
        print(f"Passed  test_load_config for chan: {chan}")
      
    def test_save_to_bms(self, msg, atype):                
        print("===================")
        chan = msg["CHAN"]
        msg["TYPE"]=atype
        if atype =='c':
            # update start_message to be a calibration...
            msg['PURPOSE']=201   # add back in for test
        elif atype == 'm':
            # update start_message to be a measurement...
            msg['PURPOSE']=101 
        print(f"testing save_to_bms() for a record of type {atype} on chan: {chan}")
        # everything else should be the same...
        msg["SENDER_ID"]="adc"           # add back in for test
        ts= round(dbi._timestamp(), 3)             # for tests use the timestamp of the dbi to allow user to verify recent saves.
        msg['TIMESTAMP']=ts
        print(f"msg to save: {msg}")
        #save a record to to db table bms...
        dbi.save_to_bms(msg)
        #read from db to check for last record.
        records = dbi.list_bms(1, atype)
        print(f" len(records) : {len(records)}")
        lenc= len(records)
        if lenc < 1:
            print("no records")
            print("Failed")
        else:
            last_record = BMS(*records[-1])
            #print(f" type (last_record): {type(last_record)}")
            print(f" Last Record : {last_record}")
            #print(f" msg.vm: {msg['VM_MEAN'] }  type: {type(msg['VM_MEAN'])}")
            assert last_record.TYPE ==atype , f" Wrong type: {last_record.TYPE } is not 'atype'  "
            last_record.VM_MEAN   == msg["VM_MEAN"], f"vm is different from input to saved record {last_record.VM_MEAN}"
            assert ts == round(float(last_record.TIMESTAMP),3) , f" Timestamp of record: {last_record.TIMESTAMP} differs from ts {ts}"

    def test_list_records(self,chan, atype):
        print("===================")
        print(f"testing list_records({chan})")
        records = dbi.list_records(chan)
        lenc=len(records)
        print(f"Number of calibration records on chan {chan}: {lenc} ")
        if lenc > 1:
            print(f"records:  {records}")
            last_record = BMS(*records[-1])
            #print(f" records[-1]: {records[-1]}")
            assert last_record.TYPE == 'c' , f" type: {last_record.type} is not 'c'"
        print(f"Passed test_list_records on chan: {chan}")
        
  
    def test_list_records(self, chan, atype):
        print("===================")
        if atype =='m':
            _type = 'measurements'
        elif atype == 'c':
            _type = 'calibrations'
        print(f"testing list_records() on chan {chan} for {_type}")
        records = dbi.list_bms(chan, atype)
        lenm=len(records)
        if lenm < 1:
            print( "no records")
            print(f"Passed on chan {chan}")
        else:
            print(f"records:  {records}")
            last_record = BMS(*records[-1])
            #print(f" records[-1]: {records[-1]}")
            assert last_record.TYPE == atype , f" Type: {last_record.type} is not {atype}"
            print(f"Number of measurement records: {lenm} ")

            print(f"Passed  test_list_records on chan: {chan} for {_type}")

    def test_update_lut(self, chan):
        print("===================")
        print(f"testing update_lut({chan}) by adding  .0001 to first vin in  LUT, update db, test update, then update to original vin and test the restoration")
        diff=0.0001
        # get the lut, find first vm, select lut_item;  add diff
        lut=dbi.get_lut(chan)
        vm1=min(lut.keys())
        li=LUT_ITEM(*dbi.get_lut_pair(chan, vm1))
        vin_new = li.VIN + diff
        # update LUTS table with vin_new...
        li2=LUT_ITEM(li.ID, li.APP_ID, li.VERSION, li.CHAN, li.VM, vin_new)
        dbi.update_lut_pair(li2)
        # test to ensure update:
        li3= LUT_ITEM(*dbi.get_lut_pair(chan, vm1))
        assert li3.VIN == vin_new, f"Updated vin was not persisted {li3.VIN} not equal to {li2.VIN} "
        # restore previous vin value and test to ensure restoration
        dbi.update_lut_pair(li)
        li4 =  LUT_ITEM(*dbi.get_lut_pair(chan, vm1))
        assert li4.VIN == li.VIN, f"First vin was not restored. {li4.VIN} does not equal {li.VIN}"
          
        print(f"Passed test_update_lut({chan}) ")
        
    


    def test_stats(self, chan):
        global samps
        '''Tests the computation of mean, sd, interpolation,'''
        print("===================")
        print(f"testing stats({chan})")
        eps = 1e-6
        samps = json.loads(samples[chan])
        print(f" type of samps[{chan}]: {type(samps[chan])}" )

        stat = dbi.stats(chan, samps)
        print(f" a2d_mean: {stat.a2d}  vm_mean: {stat.vm} vm_sd: {stat.vm_sd}  vb: {stat.vb}") 
        assert stat.a2d - answers[chan].a2d < eps , f" A2d mean count is wrong: {stat.a2d}. Should be: {answers[chan].a2d}'"
        assert stat.vm - answers[chan].vm < eps , f" vm  is wrong: {stat.vm}. Should be: {2.655}'"
        assert stat.vm_sd - answers[chan].vm_sd < eps , f" vm_sd  is wrong: {stat.vm_sd}. Should be: {answers[chan].vm_sd }'"
        assert stat.vb - answers[chan].vb <eps , f" vb is wrong: {stat.vb}. Should be: {answers[chan].vb}'"

        print(f"Passed  test_stats[{chan}]")

    def test_a2d_bms_sync(self):
        '''ensure that the last A2d record  has bms_id = bms.id of last bms record '''
        print("======================")
        print("Testing bms.id sync with A2D.bms_id")
        bms_id, a2d_bms_id = dbi.check_bms_id_in_a2d()
        assert bms_id ==a2d_bms_id, f"The a2d.bms_id {a2d_record[1]} should equal bms.id {bms_record[0]}"     
        print("Passed test:  test_a2d_bms_sync")
        
    def test_lut_limits(self,chan):
        '''If a vm is within 1/2 of a vm step, then use the key at that end of the lut'''
        print("===================")
        print(f"Testing Lut Limits... chan {chan}")
        lut= dbi.get_lut(chan)
        vm_lo= min(lut.keys())
        vm_hi= max(lut.keys())           
        ok_lo_vm = vm_lo   
        ok_hi_vm = vm_hi
        too_low_vm = vm_lo - 0.12345
        too_high_vm = vm_hi +0.12345

        eps = 1e-6
        print(f" for vm= ok_lo_vm = {ok_lo_vm}")
        vm,lut = dbi.matchesboundary(chan, ok_lo_vm, dbi.version)
        if vm is not None:
            print("vm: " , vm)
            assert abs(vm - vm_lo) < eps, f"vm: {vm} is incorrect. It should be {vm_lo}"
        print(f" for vm= ok_hi_vm = {ok_hi_vm}")
        vm, lut = dbi.matchesboundary(chan, ok_hi_vm , dbi.version)
        print("vm: ", vm)
        if vm is not None:
            print("vm: " , vm)
            assert abs(vm - vm_hi ) < eps,  "vm is incorrect. "
        vm, lut = dbi.matchesboundary(chan, too_low_vm, dbi.version)
        assert vm is None, "Error, should return None"
        vm, lut = dbi.matchesboundary(chan, too_high_vm, dbi.version)
        assert vm is None, "Error, should return None"
        
        print()
        print(f"Passed  test_lut_limits chan {chan}")
        
    def test_call_function(self, code, arglist):
            print("===================")
            print(f"Testing call_function: code: {code} function: { dbi.funct_dict[code].__name__ }  arglist: {arglist}")
            print(dbi.funct_dict[code] ( *arglist))
        
testdbi=Test_DBI()
#start_msg is defined near line 18
print(" =========Tests Begin =======================")
#TODO 7: Fix tests broken by schema change: They are commented out.
testdbi.test_get_lut(0)
testdbi.test_get_lut(1)
testdbi.test_get_lut(2)
testdbi.test_load_config(1,0)
testdbi.test_load_config(1,1)
testdbi.test_load_config(1,2)
testdbi.test_cols_vals(deepcopy(start_msg))
testdbi.test_save_to_bms(deepcopy(start_msg),'c')                #calibrations
testdbi.test_save_to_bms(deepcopy(start_msg),'m')     # measurements
testdbi.test_list_records(0, 'm')
testdbi.test_list_records(1, 'm')
testdbi.test_list_records(2, 'm')
testdbi.test_list_records(0,'c')
testdbi.test_list_records(1,'c')
testdbi.test_list_records(2,'c')
testdbi.test_update_lut(0)   
testdbi.test_update_lut(1)
testdbi.test_update_lut(2)
testdbi.test_lut_limits(0)
testdbi.test_lut_limits(1)
testdbi.test_lut_limits(2)
testdbi.test_a2d_bms_sync()
testdbi.test_call_function(330, [0, 'm'])
testdbi.test_call_function(330, [0, 'c'])
testdbi.test_call_function(330, [1, 'm'])
testdbi.test_call_function(330, [1, 'c'])
testdbi.test_call_function(330, [2, 'm'])
testdbi.test_call_function(330, [2, 'c'])
testdbi.test_call_function(340, [5])
testdbi.test_call_function(310, [0])
testdbi.test_call_function(310, [1])
testdbi.test_call_function(310, [2])
testdbi.test_call_function(350, [0])
testdbi.test_call_function(350, [1])
testdbi.test_call_function(350, [2])

'''
#testdbi.test_timestamp()
'''


    
