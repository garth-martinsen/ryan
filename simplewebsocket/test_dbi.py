# file test_dbi.py  Given a msg, save the bms in the msg to BMS table in database rt_db.   Run in Python3

from database_interface import DatabaseInterface
from database_interface_config import Config, LUT, BMS, BMS_FIELDS, CONFIG_FIELDS
from dbi_records import  configs,  bms
#from lut_convert import LutConvert as LC
from collections import OrderedDict
from copy import deepcopy

app_id=1
version=3
# samps = '[21357, 21354, 21351, 21353, 21355, 21357, 21351, 21357, 21351, 21355, 21357, 21353, 21356, 21358, 21356, 21358, 21357, 21355, \
# 21353, 21355, 21355, 21355, 21355, 21356, 21351, 21358, 21356, 21358, 21358, 21353, 21352, 21358, 21358, 21353, 21355, 21357, 21356, \
# 21353, 21354, 21356, 21358, 21356, 21355, 21358, 21351, 21351, 21354, 21356, 21351, 21352, 21354, 21355, 21355, 21352, 21354, 21358, \
# 21355, 21356, 21358, 21357, 21356, 21357, 21352, 21353]'

dbi = DatabaseInterface(app_id,version)

#6/6/26: BMS_FIELDS = ("ID", "MSGID", "VERSION", "TIMESTAMP", "TYPE", "CHAN", "A2D_MEAN", "VM_MEAN", "VM_SD", "VB", "VIN", "ERROR", "SAMP_SZ", "DISCARD_SZ", "KEEP_SZ", "SAMPLES")

# missing until computed: "A2D_MEAN", "VM_MEAN", "VM_SD", "VB", "ERROR"
start_msg=  {'PURPOSE':101, 'MSGID': 5010, "VERSION": 3, 'TIMESTAMP': '2026-2-23  15:31:21.54',  'TYPE': 'm', 'CHAN': 1,
                       "A2D_MEAN": 21355.0, "VM_MEAN": 2.669375 , "VM_SD" : 0.00028038, "VB": 7.9747, "ERROR": 0.02529, "VIN": 7.97,
                       "SAMP_SZ": 64,"DISCARD_SZ": 2, "KEEP_SZ": 62,
               "SAMPLES":  '[21357, 21354, 21351, 21353, 21355, 21357, 21351, 21357, 21351, 21355, 21357, 21353, 21356, 21358, \
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
    def test_get_lut0(self, chan):
        print("===================")
        print("testing get_lut(0)")
        chan = 0
        lut= dbi.get_lut(chan,dbi.version)
        lut=OrderedDict(lut)
        print(f"lut[0]: {lut}")
        print(f"type of lut:  { type(lut)} , lut: { lut} ")
        firstval=3.0
        lastval = 4.5
        assert lut[2.2507] == firstval  , f"{ lut[2.0644] } is wrong ; it should be first value in lut : {firstval} "
        assert lut[3.3761] == lastval ,   f"{ lut[3.0966] } is wrong ; it should be  last value in lut : {lastval}"
         
        print("Passed  test_get_lut0")
         
 #for the given channel 1. Testing is done on 1st and  last pairs...
    def test_get_lut1(self,chan):
        print("===================")
        print("testing get_lut1(1)")
        chan = 1
        lut= dbi.get_lut(chan, dbi.version)
        lut=OrderedDict(lut)
        print(f"lut[0]: {lut}")
        print(f"type of lut:  { type(lut)} , lut: { lut} ")
        firstval=6.0
        lastval = 9.0
        assert lut[2.0084] == firstval  , f"{ lut[2.0644] } is wrong ; it should be first value in lut : {firstval} "
        assert lut[3.0126] == lastval ,   f"{ lut[3.0966] } is wrong ; it should be  last value in lut : {lastval}"
         
        print("Passed  test_get_lut1")

    # for channel 2 lut. Testing is done on1st and  last pairs...
    def test_get_lut2(self, chan) :
        '''Selects the lut for the given channel 2. '''
        print("===================")
        print("testing get_lut2(2)")
        chan=2
        lut= dbi.get_lut(chan, dbi.version)
        lut=OrderedDict(lut)
        print(f"lut[0]: {lut}")
        print(f"type of lut:  { type(lut)} , lut: { lut} ")
        firstval=9.0
        lastval = 13.5
        assert lut[2.2539] == firstval  , f"{ lut[2.0644] } is wrong ; it should be first value in lut : {firstval} "
        assert lut[3.3809] == lastval ,   f"{ lut[3.0966] } is wrong ; it should be  last value in lut : {lastval}"
         
        print("Passed  test_get_lut2")
       
    #TODO 3 DONE  : Finish test_load_config
     #TODO 6: This test queries the db. Not good practice for unit tests...   
    def test_load_config(self, app_id, chan):
        '''fetches the  record from the CONFIG table for the chan'''
        print("===================")
        print(f"testing load_config() for chan: {chan}")
        # get config from the databaseInterface on table config.
        record = dbi.load_config(app_id, chan, dbi.version)
        print(f"type(record):  {type(record)} config record for chan :{chan}: {Config(*record[0])} ")
        cfg= Config(*record[0])
        #dbi.cfgs[chan]=cfg
        print(f" config[0]: {configs[0]}")
        print(f" config[1]: {configs[1]}")
        print(f" config[2]: {configs[2]}")
        #assert len(records) == 3, "There should be only 3 records, one for each channel"
       
        EPS=1e-6
        if chan == 0:
            print(f"r1 {cfg.R1}  R2: {cfg.R2}")
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
            print(f" chan 2 r1: {cfg.R1}  r2: {cfg.R2}")
            assert cfg.CHAN_DESC == 'Three Cells 9.0-13.5V', "Wrong description"
            assert cfg.R1== 301400,f"Wrong value for r1. Should be: {cfg.R1}"
            assert cfg.R2 == 100700,  f"Wrong value for r2. Should be: {cfg.R2}"
            assert cfg.C1 - 1.0e-07 < EPS, f"Wrong value for C1. Should be {1e-07}"
        print(f"Passed  test_load_config for chan: {chan}")
     
#     def test_timestamp(self):
#         print("===================")
#         print("testing timestamp()")
#         ts= dbi._timestamp()
#         print(f"timestamp: {ts}")
#        
#         # compare timestamps without seconds
#         assert last.timestamp[:-1] == ts[:-1], f" Timestamp is incorrect! {ts} from last record:{last.timestamp}" 
#         print("Passed")
   
     #TODO 1 : Fix the BMS namedtuple so last record is interpreted correctly...
     #TODO 2: The BMS is scrambled. Find out why. Look at test.dbi.save_calibration outputs. timestamp and cfg_id are swapped.
     #TODO 4: 3/11/26: Finish calibration test. BMS and A2D tables are new or restructured...
    def test_save_calibration(self, msg):
        print("===================")
        print("testing save_calibration()")
        msg['PURPOSE']=201   # add back in for test
        msg["CHAN"]=1            # add back in for test
        msg["SENDER_ID"]="adc"           # add back in for test
        msg["MSGID"]= 5010
        msg["VERSION"]=3
        msg['DISCARD_SZ']=2
        msg['SAMP_SZ'] = 64
        msg["KEEP_SZ"]= 62
        ts= dbi._timestamp()
        msg['TIMESTAMP']=ts
        msg['TYPE']='c'
        #save to db
        cols, vals = dbi.save_calibration(msg)
         #read from db
        records = dbi.list_calibrations(1)
        print(f" len(records) : {len(records)}")
        lenc= len(records)
        if lenc < 1:
            print("no records")
            print("Failed")
        else:
            last_record = BMS(*records[-1])
            print(f" type (last_record): {type(last_record)}")
            print(f" Last Record : {last_record}")
            print(f" msg.vm: {msg['VM_MEAN'] }  type: {type(msg['VM_MEAN'])}")
            assert last_record.TYPE == 'c' , f" Wrong type: {last_record.TYPE } is not 'c'  "
            last_record.VM_MEAN   == msg["VM_MEAN"], f"vm is different from input to saved record {last_record.VM_MEAN}"
            assert ts == last_record.TIMESTAMP , f" Timestamp of record: {last_record.TIMESTAMP} differs from ts {ts}"
            print("Passed  test_save_calibration")


    def test_save_measurement(self,msg):
        global start_msg
        print("start_msg: ", start_msg)
        print("===================")
        print("testing save_measurement()")
        chan=msg["CHAN"]
        msg["TYPE"]='m'
        msg["MSGID"]= 5010
        msg["VERSION"]=3
        msg['DISCARD_SZ']=2
        msg['SAMP_SZ'] = 64
        msg["KEEP_SZ"]= 62
        msg['PURPOSE']=101   # add back in for test
        msg['SENDER_ID']="adc_client"   # add back in for test
        msg['VM_MEAN']=2.669375
        if "bms_id" in msg: msg.pop("bms_id")
        ts= dbi._timestamp()
        msg['TIMESTAMP']=ts
        # save to db
        print(f"save_measurement msg: {msg}")
        cols,vals = dbi.save_measurement(msg)
        # read from db
        records = dbi.list_measurements(chan)
        lenm = len(records)
        eps = 1e-6
        if lenm <1:
            print("no records")
            print("Failed")
        else:
            print(f" len(records) {len(records)}")
            last_record = BMS(*records[-1])     # this is creating errors b ecause the BMS order is not used correctly
           # print(f" Last Record : {last_record}")
            print(f" Last Record : {last_record}")
            #print(f"Last record type is: {last_record.type} ")
#             print( "last_record     msg attribute" )
#             print( f" {last_record.TYPE} ..........  {msg['TYPE']}")
#             print( f" {last_record.VM_MEAN}.......... { msg['VM_MEAN']}")
#             print( f" {last_record.TIMESTAMP} ..........{msg['TIMESTAMP']}")
#             assert last_record.TYPE == 'm' , f" Type: {last_record.TYPE} should be 'm' "
            assert  last_record.VM_MEAN - msg['VM_MEAN']  < eps, f" Vm: {last_record.VM_MEAN} is not  equal to: {msg.VM_MEAN}"
            assert last_record.TIMESTAMP == ts, f" Timestamp is wrong.  {last_record.TIMESTAMP} differs from ts : {ts}"
            print( "Passed  test_save_measurement")

    def test_list_calibrations(self):
        print("===================")
        print("testing list_calibrations()")
        records = dbi.list_calibrations(1)
        lenc=len(records)
        print(f"records:  {records}")
        last_record = BMS(*records[-1])
        #print(f" records[-1]: {records[-1]}")
        assert last_record.TYPE == 'c' , f" type: {last_record.type} is not 'c'"
        print(f"Number of calibration records: {lenc} ")
        print("Passed test_list_calibrations")
        
  
    def test_list_measures(self):
        print("===================")
        print("testing list_measures() on chan 1")
        records = dbi.list_measurements(1)
        lenm=len(records)
        if lenm < 1:
            print( "no records")
            print("Passed")
        else:
            print(f"records:  {records}")
            last_record = BMS(*records[-1])
            #print(f" records[-1]: {records[-1]}")
            assert last_record.TYPE == 'm' , f" Type: {last_record.type} is not 'm'"
            print(f"Number of measurement records: {lenm} ")

            print("Passed  test_list_measures")

    def test_update_lut(self, chan):
        print("===================")
        print("testing update_lut(chan) by adding  .0001 to first and last values in LUT, saving to db, testing update, then restoring")        
        lut= dbi.get_lut(chan, dbi.version)
        first_vm= min(lut.keys())
        last_vm= max(lut.keys())
        # save to check restoration
        first_vin = lut[first_vm]
        last_vin= lut[last_vm]
        # modify the first and last vin by adding 0.0001 to each
        updated_first_vin = first_vin + 0.0001
        updated_last_vin = last_vin  + 0.0001
        lut[first_vm]= updated_first_vin
        lut[last_vm]= updated_last_vin
        #print("\tafter adding .0001: ", lut)
        # get ids for first and last
        first_id, vm, vin, version = dbi.get_lut_row(chan, first_vm)
        last_id, vm, vin, version = dbi.get_lut_row(chan, last_vm)
        # update the first and the last pairs in the lut.  saving lut_ts to config. is part of dbi.update_lut_pair()
        dbi.update_lut_pair( chan, first_id, first_vm, updated_first_vin)
        dbi.update_lut_pair( chan, last_id, last_vm, updated_last_vin)
        # check to see if lut was updated with +0.0001
        lut= dbi.get_lut(chan, dbi.version)
        eps=1e-6
        print("\tlut retrieved after update by 0.0001: " , lut)
        assert lut[first_vm] - updated_first_vin < eps, f" First vin was not updated. should be: {updated_first_vin}"
        assert lut[last_vm] - updated_last_vin < eps, f" Last vin was not updated. should be: {updated_last_vin}"
        #restore lut to original state
        dbi.update_lut_pair(chan, first_id, first_vm, lut[first_vm] -  0.0001)
        dbi.update_lut_pair(chan, last_id, last_vm, lut[last_vm] -  0.0001)
        # check restoration
        lut=dbi.get_lut(chan, dbi.version)
        assert lut[first_vm] == first_vin , f" First vin was not restored. should be: {first_vin}"
        assert lut[last_vm] == last_vin , f" Last vin was not restored. should be: {last_vin}"
          
        print(f"Passed test_update_lut({chan}) ")
        
    

# TODO 5: Find error in updating lut . Expect problem is in dbi.update_lut(msg)

#         dbi.update_lut(msg, dbi.version)  # changing vals on first and last
#         lut = dbi.get_lut(0, dbi.version)
#         original_first = lut[2.2507]
#         original_last = lut[3.3761]
#         print(f"\t Original first and last: {original_first} {original_last}")
#         cfg= Config(*dbi.load_config(1,0,dbi.version)[0])
#         eps = 1e-6
#         print(f"cfg: {cfg}  lut: {lut}")
#         lut_ts = cfg.LUT_TS
#         lut[2.2507]=lut[2.2507] + 0.0001
#         lut[3.3761]= lut[3.3761] + 0.0001
#         print("\t Updated first and last: " , updated_first, updated_last)
#         
#         print(f"lut[2.2507]:  {lut[2.2507]}  lut[3.3761] : {lut[3.3761]}")
#         assert lut_ts[:-1] == ts[:-1], f"Update of LUT should have correct timestamp {ts}  found: {lut_ts}."
#         assert lut[2.2507] - first <eps, "Value of first lut pair was not updated to {first}"
#         assert lut[3.3761] - last <eps, "Value of last lut pair was not updated to {last}"
#         print("update_lut(...) Passed")
#         # restoring first & last vals... 
#         print("Restoring original values")
#         first = 3.0
#         last = 4.5
#         lut0[2.2507]=first
#         lut0[3.0966]=  last
#         msg["LUT"]=str(lut0)
#         ts = dbi._timestamp()
#         msg["chan"] = 0
#         print (f"msg: {msg} ")
#         dbi.update_lut(msg,dbi.version)
#         print()
#         print("Passed  test_update_lut_0")
#         

    def test_stats(self):
        '''Tests the computation of mean, sd, interpolation,'''
        print("===================")
        print("testing stats()")
        eps = 1e-6
        stat0 = dbi.stats(0, samps)     
        assert stat0.a2d- 21655 < eps , f" A2d mean count is wrong: {stat.a2d}. Should be: {21655.4}'"
        assert stat0.vm - 2.075< eps , f" vm  is wrong: {stat.vm}. Should be: {2.655}'"
        assert stat0.vm_sd - 0.00028< eps , f" vm_sd  is wrong: {stat.vm_sd}. Should be: {0.00029}'"
        assert stat0.vb- 3.7 <eps , f" vb is wrong: {stat.vb}. Should be: {3.7}'"

        print("Passed  test_stats")
     # TODO7: Remove the complexity of fudging boundaries, too complex... Also expand so it covers all channels... 
    def test_lut_limits(self,chan):
        '''If a vm is within 1/2 of a vm step, then use the key at that end of the lut'''
        print("===================")
        print(f"Testing Lut Limits... chan {chan}")
        lut= dbi.get_lut(chan, dbi.version)
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
        print("Passed  test_lut_limits")
        
testdbi=Test_DBI()
#start_msg is defined near line 18
#TODO 8: Fix: save_calibration() and save_measurement() values and cols is confused.


testdbi.test_get_lut0(0)
testdbi.test_get_lut1(1)
testdbi.test_get_lut2(2)
testdbi.test_load_config(1,0)
testdbi.test_load_config(1,1)
testdbi.test_load_config(1,2)
testdbi.test_cols_vals(deepcopy(start_msg))
testdbi.test_save_calibration(deepcopy(start_msg))
testdbi.test_save_measurement(deepcopy(start_msg))
testdbi.test_list_measures()
testdbi.test_list_calibrations()
testdbi.test_update_lut(2)
testdbi.test_lut_limits(0)

#testdbi.test_timestamp()



    
