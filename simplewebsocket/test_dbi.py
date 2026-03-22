# file test_dbi.py  Given a msg, save the bms in the msg to BMS table in database rt_db.   Run in Python3

from database_interface import DatabaseInterface
from database_interface_config import Config, LUT, BMS
from dbi_records import  configs,  bms
from lut_convert import LutConvert as LC
from collections import OrderedDict
from copy import deepcopy

app_id=1
samps = '[21357, 21354, 21351, 21353, 21355, 21357, 21351, 21357, 21351, 21355, 21357, 21353, 21356, 21358, 21356, 21358, 21357, 21355, \
21353, 21355, 21355, 21355, 21355, 21356, 21351, 21358, 21356, 21358, 21358, 21353, 21352, 21358, 21358, 21353, 21355, 21357, 21356, \
21353, 21354, 21356, 21358, 21356, 21355, 21358, 21351, 21351, 21354, 21356, 21351, 21352, 21354, 21355, 21355, 21352, 21354, 21358, \
21355, 21356, 21358, 21357, 21356, 21357, 21352, 21353]'

dbi = DatabaseInterface(app_id)
lc=LC()
#bms_fields:        'id',      'timestamp',             'type', 'chan', 'FSR', 'LSB', 'vin', 'error', 'a2d', 'vm', 'vm_sd', 'vb', 'samples')
start_msg=  {'purpose':101, 'timestamp': '2026-2-23  15:31:21.54',  'type': 'm', 'chan': 1, "FSR": 4.095, "LSB":0.00012496948,"vin": 8.5256,"samples":  '[21357, \
21354, 21351, 21353, 21355, 21357, 21351, 21357, 21351, 21355, 21357, 21353, 21356, 21358, 21356, 21358, 21357, 21355, \
21353, 21355, 21355, 21355, 21355, 21356, 21351, 21358, 21356, 21358, 21358, 21353, 21352, 21358, 21358, 21353, 21355, 21357, 21356, \
21353, 21354, 21356, 21358, 21356, 21355, 21358, 21351, 21351, 21354, 21356, 21351, 21352, 21354, 21355, 21355, 21352, 21354, 21358, \
21355, 21356, 21358, 21357, 21356, 21357, 21352, 21353] '}

{"purpose":201,"timestamp": f"{dbi._timestamp()}", "type": 'c', "chan": 1,   "a2d": 0, "vm": 0, "vm_sd": 0,  "vb": 0, "vin": 8.635, "error": 0.0, "sample_period":0.015625, "store_time": 0.000445, "gate_time": 1.00034 , "samples": f"{samps}"}     

class Test_DBI:
    def __init(self):
        self.one=1
        self.cfgs=None

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
        print("Passed")
     
    #for the given channel 0. Testing is done on 1st and  last pairs....'''
    '''Selects the lut for the channel 0. '''
    def test_get_lut0(self, chan):
        print("===================")
        print("testing get_lut(0)")
        chan = 0
        lut= dbi.get_lut(chan)
        lut=OrderedDict(lut)
        print(f"lut[0]: {lut}")
        print(f"type of lut:  { type(lut)} , lut: { lut} ")
        firstval=3.0
        lastval = 4.5
        assert lut[2.0644] == firstval  , f"{ lut[2.0644] } is wrong ; it should be first value in lut : {firstval} "
        assert lut[3.0966] == lastval ,   f"{ lut[3.0966] } is wrong ; it should be  last value in lut : {lastval}"
         
        print("Passed")
         
 #for the given channel 1. Testing is done on 1st and  last pairs...
    def test_get_lut1(self,chan):
        print("===================")
        print("testing get_lut1(1)")
        chan = 1
        lut= dbi.get_lut(chan)
        lut=OrderedDict(lut)
        print(f"lut[0]: {lut}")
        print(f"type of lut:  { type(lut)} , lut: { lut} ")
        firstval=6.0
        lastval = 9.0
        assert lut[1.8795] == firstval  , f"{ lut[2.0644] } is wrong ; it should be first value in lut : {firstval} "
        assert lut[2.8192] == lastval ,   f"{ lut[3.0966] } is wrong ; it should be  last value in lut : {lastval}"
         
        print("Passed")

    # for channel 2 lut. Testing is done on1st and  last pairs...
    def test_get_lut2(self, chan) :
        '''Selects the lut for the given channel 2. '''
        print("===================")
        print("testing get_lut2(2)")
        chan=2
        lut= dbi.get_lut(chan)
        lut=OrderedDict(lut)
        print(f"lut[0]: {lut}")
        print(f"type of lut:  { type(lut)} , lut: { lut} ")
        firstval=9.0
        lastval = 13.5
        assert lut[2.2337] == firstval  , f"{ lut[2.0644] } is wrong ; it should be first value in lut : {firstval} "
        assert lut[3.3506] == lastval ,   f"{ lut[3.0966] } is wrong ; it should be  last value in lut : {lastval}"
         
        print("Passed")
       
    #TODO 3 DONE  : Finish test_load_config  
    def test_load_config(self):
        '''fetches the 3 records from the CONFIG table for use in a class'''
        print("===================")
        print("testing load_config()")
        records = dbi.load_config(app_id)
        print("config records: ", records)
        configs:[Config, Config, Config]=[[],[],[]]
        for i in range(len(records)):
           configs[i]=Config(*records[i])
        print(f" config[0]: {configs[0]}")
        print(f" config[1]: {configs[1]}")
        print(f" config[2]: {configs[2]}")
        assert len(records) == 3, "There should be only 3 records, one for each channel"
        assert configs[0].chan_desc ==  '3-4.5V circuit chan(0)' , "Wrong description"
        assert configs[1].chan_desc == '6-9V circuit chan(1)' , "Wrong description"
        assert configs[2].chan_desc == '9-13.5 V circuit chan(2)', "Wrong description"
        assert configs[0].C1 == 1e-07
        assert configs[0].r1 == 99300.0, f"Wrong value for r1. Should be: {configs[0].r1}"
        print("Passed")
     
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
        msg['purpose']=201   # add back in for test
        msg["chan"]=1            # add back in for test
        msg["sender_id"]="adc"           # add back in for test
        msg["msg_id"]=1234    # add back in for test
        ts= dbi._timestamp()
        msg['timestamp']=ts
        msg['type']='c'
        #save to db
        dbi.save_calibration(msg)
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
            print(f" msg.vm: {msg['vm'] }  type: {type(msg['vm'])}")
            assert last_record.type == 'c' , f" Wrong type: {last_record.type } is not 'c'  "
            last_record.vm   == msg["vm"], f"vm is different from input to saved record {last_record.vm}"
            assert ts == last_record.timestamp , f" Timestamp of record: {last_record.timestamp} differs from ts {ts}"
            print("Passed")


    def test_save_measurement(self,msg):
        global start_msg
        print("start_msg: ", start_msg)
        print("===================")
        print("testing save_measurement()")
        chan=msg["chan"]
        msg["type"]='m'
        msg['purpose']=101   # add back in for test
        msg['sender_id']="adc_client"   # add back in for test
        msg['msg_id']="adc_client"   # add back in for test
        if "bms_id" in msg: msg.pop("bms_id")
        ts= dbi._timestamp()
        msg['timestamp']=ts
        # save to db
        print(f"save_measurement msg: {msg}")
        dbi.save_measurement(msg)
        # read from db
        records = dbi.list_measurements(chan)
        lenm = len(records)
        if lenm <1:
            print("no records")
            print("Failed")
        else:
            print(f" len(records) {len(records)}")
            last_record = BMS(*records[-1])
            print(f" Last Record : {last_record}")
            #print(f"Last record type is: {last_record.type} ")
            assert last_record.type == 'm' , f" Type: {last_record.type} should be 'm' "
            assert last_record.vm ==msg["vm"], f" Vm: {last_record['vm']} is not  equal to: {msg['vm']}"
            assert last_record.timestamp == ts, f" Timestamp is wrong.  {last_record.timestamp} differs from ts : {ts}"
            print( "Passed")

    def test_list_calibrations(self):
        print("===================")
        print("testing list_calibrations()")
        records = dbi.list_calibrations(0)
        lenc=len(records)
        print(f"records:  {records}")
        last_record = BMS(*records[-1])
        #print(f" records[-1]: {records[-1]}")
        assert last_record.type == 'c' , f" type: {last_record.type} is not 'c'"
        print(f"Number of calibration records: {lenc} ")
        print("Passed")
        
  
    def test_list_measures(self):
        print("===================")
        print("testing list_measures()")
        records = dbi.list_measurements(0)
        lenm=len(records)
        if lenm < 1:
            print( "no records")
            print("Passed")
        else:
            print(f"records:  {records}")
            last_record = BMS(*records[-1])
            #print(f" records[-1]: {records[-1]}")
            assert last_record.type == 'm' , f" Type: {last_record.type} is not 'm'"
            print(f"Number of measurement records: {lenm} ")

            print("Passed")

    def test_update_lut_0(self):
        print("===================")
        print("testing update_lut0()")
        msg = {}
        #add .0001 to first and last values in LUT  {2.375: 3.001, and  3.8: 4.5001} and save
        lut0= dbi.get_lut(0)
        first = 3.0001
        last = 4.5001
        lut0[2.0644]=first
        lut0[3.0966]=  last
        print("after adding .0001: ", lut0)
        msg["LUT"]=str(lut0)
        ts = dbi._timestamp()
        msg["chan"] = 0
        print (f"msg: {msg} ")

        dbi.update_lut(msg)  # changing vals on first and last
# TODO 5: Find error in updating lut . Expect problem is in dbi.update_lut(msg)
        lut = dbi.get_lut(0)
        cfg= Config(*dbi.load_config(1)[0])
        eps = 1e-6
        print(f"cfg: {cfg}  lut: {lut}")
        lut_ts = cfg.LUT_TS
        print("testing for updated first and last: " , first, last)
        assert lut_ts[:-1] == ts[:-1], f"Update of LUT should have correct timestamp {ts}  found: {lut_ts}."
        assert lut[2.0644] - first <eps, "Value of first lut pair was not updated to {first}"
        assert lut[3.0966] - last <eps, "Value of last lut pair was not updated to {last}"
        print("Passed")
        # restoring first & last vals... 
        print("Restoring original values")
        first = 3.0
        last = 4.5
        lut0[2.0644]=first
        lut0[3.0966]=  last
        msg["LUT"]=str(lut0)
        ts = dbi._timestamp()
        msg["chan"] = 0
        print (f"msg: {msg} ")
        dbi.update_lut(msg)
        print()
        print("Passed")
        

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

        print("Passed")
        
    def test_lut_limits(self):
        '''If a vm is within 1/2 of a vm step, then use the key at that end of the lut'''
        chan = 0
        vd_fract = 0.688128140703518  # from config record for chan 0
        vin_step = 0.1                               # every 0.1v is next vin
        vm_lo = 2.0644 - vd_fract *vin_step/2     # vm for lowest vin, 3.0V
        vm_hi = 3.0966 + vd_fract *vin_step/2    # vim for highest vin, 4.5v
        too_low_vm = vm_lo -  3e-6
        too_hi_vm = vm_hi +   3e-6
        ok_lo_vm = vm_lo   
        ok_hi_vm = vm_hi 
        eps = 1e-6
        print(" for vm= ok_lo_vm")
        vm,lut = dbi.matchesboundary(chan, ok_lo_vm + .0003)
        if vm is not None:
            print("vm: " , vm)
            assert abs(vm - 2.0644) < eps, "vm is incorrect. "
        print(" for vm= ok_hi_vm")
        vm, lut = dbi.matchesboundary(chan, ok_hi_vm - 0.0003 )
        print("vm: ", vm)
        if vm is not None:
            print("vm: " , vm)
            assert abs(vm - 3.0966 ) < eps,  "vm is incorrect. "
        print(" for vm= too_low_vm")
        vm , lut = dbi.matchesboundary(chan, too_low_vm )
        print("vm: ", vm)
        assert vm == None, " vm should be None "
        print(" for vm= too_hi_vm ")
        vm , lut = dbi.matchesboundary(chan, too_hi_vm )
        print("vm: ", vm)
        assert vm == None, " vm should be None "
        print()
        print("Passed")
        
testdbi=Test_DBI()
#start_msg is defined near line 18
testdbi.test_get_lut0(0)
testdbi.test_get_lut1(1)
testdbi.test_get_lut2(2)
testdbi.test_load_config()
testdbi.test_cols_vals(deepcopy(start_msg))
testdbi.test_save_calibration(deepcopy(start_msg))
testdbi.test_save_measurement(deepcopy(start_msg))
#testdbi.test_timestamp()
testdbi.test_list_measures()
testdbi.test_list_calibrations()
testdbi.test_update_lut_0()
testdbi.test_lut_limits()


    
