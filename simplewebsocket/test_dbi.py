# file test_dbi.py  Given a msg, save the bms in the msg to BMS table in database rt_db.   Run in Python3

from database_interface import DatabaseInterface
from database_interface_config import Config, LUT_INFO
import ast

msg={"purpose":201,"timestamp": "2025-8-9  17:3:57", "chan": 1,  "cfg_id": 2, "a2d": 27594.84,  "a2d_sd": 1.249841, "sample_sz": 44, "vin": 6.805,  "vm": 3.448513, "vb": 6.785102,"error": -0.01989841,"store_time" : 0.000448, "gate_time" : 1.00018, "sample_period" : 0.015625,  "keep" : [27585, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27593]}
lut0 ={ 2.375 :3.0 , 2.480494 :3.1 , 2.576982: 3.2 , 2.670677: 3.3 , 2.767054: 3.4 , 2.860863: 3.5 , 2.956999: 3.6 , 3.051115: 3.7 , 3.147765: 3.8 , 3.241461: 3.9 , 3.338363: 4.0 , 3.433948: 4.1 , 3.528541: 4.2 , 3.624836: 4.3 , 3.717937: 4.4 , 3.80: 4.5 }
dbi = DatabaseInterface((1,2,3))
cfg_ids = (1,2,3)

class test_DBI:
        
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
     
    def test_get_lut(self, chan):
        '''Selects the lut for the given channel. Testing is done on 2nd and next to last pairs...'''
        print("===================")
        print("testing get_lut()")
        record = dbi.get_lut(chan)[0]
        lut= ast.literal_eval(record.LUT)
        print("type of lut:  ", type(lut), "lut: ", lut , " lut_ts: ", record.LUT_TS)
        first=3.1
        last = 4.4
        assert lut[2.480494] == first  , f" { lut[2.480494] } is wrong 2nd value in lut"
        assert lut[3.717937] == last  ,   f" { lut[3.717937] } is wrong next to last value in lut"
         
        print("Passed")
       
    #TODO 3 DONE  : Finish test_load_config  
    def test_load_config(self):
        '''fetches the 3 records from the CONFIG table for use in a class'''
        print("===================")
        print("testing load_config()")
        records = dbi.load_config(cfg_ids)          
        print("config records: ", records)
        luts=[{},{},{}]
        for i in range(3):
            luts[i]= self._extract_lut(i, records[i].LUT)
        assert len(records) == 3, "There should be only 3 records, one for each channel"
        assert len(luts[0])== 16 , "LUT for Channel 0 should be in 1st record and have 16 pairs"
        assert len(luts[1]) == 31, "There should be 31 key-value pairs in circuit 1 lut"
        assert len(luts[2]) == 46, "There should be 46 key-value pairs in circuit 2j lut"
        assert records[0].chan_desc == '4.2V CIRCUIT CHANNEL(0)' , "Wrong description"
        print("Passed")
      
    def _extract_lut(self, chan, lut):
          '''Convert string dict into OrderedDict[ float:float] '''
          odlut= ast.literal_eval(lut)
          print("Chan: ", chan, "Type: ", type(odlut), " Len: ", len(odlut))
          return odlut
   
     #TODO 1 : Fix the BMS namedtuple so last record is interpreted correctly...
     #TODO 2: The BMS is scrambled. Find out why. Look at test.dbi.save_calibration outputs. timestamp and cfg_id are swapped.
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
        records = dbi.list_calibrations()
        print(f" len(records) : {len(records)}")
        last_record = records[-1]
        print(f" type (last_record): {type(last_record)}")
        print(f" Last Record : {last_record}")
        print(f" msg.vm: {msg['vm'] }  type: {type(msg['vm'])}")
        lr_vm = last_record.vm
        assert last_record.type == 'c' , f" Wrong type: {last_record.type } is not 'c'  "
        lr_vm  == msg["vm"], f"vm is different from input to saved record {last_record.vm}"
        assert ts == last_record.timestamp , f" Timestamp of record: {last_record.timestamp} differs from ts {ts}"
        print("Passed")

    def test_timestamp(self):
        print("===================")
        print("testing timestamp()")
        ts= dbi._timestamp()
        print(f"timestamp: {ts}")
        records = dbi.list_calibrations()
        last=records[-1]
        # compare timestamps without seconds
        assert last.timestamp[:-1] == ts[:-1], f" Timestamp is incorrect! {ts} from last record:{last.timestamp}" 
        print("Passed")
  
    def test_save_measure(self,msg):
        print("===================")
        print("testing save_measure()")
        chan=0
        msg['purpose']=101   # add back in for test
        msg['sender_id']="adc_client"   # add back in for test
        msg['msg_id']="adc_client"   # add back in for test
        msg["chan"]=0            # add back in for test
        ts= dbi._timestamp()
        msg['timestamp']=ts
        msg['type']='test_calibrate.py'
        # save to db
        dbi.save_measurement(msg)
        # read from db
        records = dbi.list_measurements(chan)
        print(f" len(records) {len(records)}")
        last_record = records[-1]
        print(f" Last Record : {last_record}")
        #print(f"Last record type is: {last_record.type} ")
        assert last_record.type == 'm' , f" Type: {last_record.type} should be 'm' "
        assert last_record.vm ==msg["vm"], f" Vm: {last_record['vm']} is not  equal to: {msg['vm']}"
        assert last_record.timestamp == ts, f" Timestamp is wrong.  {last_record.timestamp} differs from ts : {ts}"
        print( "Passed")

    def test_list_calibrations(self):
        print("===================")
        print("testing list_calibrations()")
        records = dbi.list_calibrations()
        last_record = records[-1]
        #print(f" records[-1]: {records[-1]}")
        assert last_record.type == 'c' , f" type: {last_record.type} is not 'c'"
        print(f"Number of calibration records: {len(records)} ")
        print("Passed")
        
  
    def test_list_measures(self):
        print("===================")
        print("testing list_measures()")
        records = dbi.list_calibrations()
        last_record = records[-1]
        #print(f" records[-1]: {records[-1]}")
        assert last_record.type == 'c' , f" Type: {last_record.type} is not 'm'"
        print(f"Number of measurement records: {len(records)} ")

        print("Passed")

    def test_update_lut_0(self):
        print("===================")
        print("testing update_lut0()")
        msg = {}
        #add .0001 to first and last values in LUT  {2.375: 3.001, and  3.8: 4.5001} and save
        first = 3.001
        last = 4.501
        lut0[2.375]=first
        lut0[3.80]=  last
        msg["LUT"]=str(lut0)
        ts = dbi._timestamp()
        msg["chan"] = 0
        print (f"msg: {msg} ")

        dbi.update_lut(msg)

        record = dbi.get_lut(0)[0]
        lut= ast.literal_eval(record.LUT)
        lut_ts = record.LUT_TS
        assert lut_ts[:-1] == ts[:-1], f"Update of LUT should have correct timestamp {ts}  found: {lut_ts}."
        assert lut[2.375] == first, "Value of first lut pair was not updated to {first}"
        assert lut[3.80]  ==  last, "Value of last lut pair was not updated to {last}"
        print("Passed")
        # restore first & last values... 
        print("Restoring original values")
        first = 3.0
        last = 4.5
        lut0[2.375]=first
        lut0[3.80]=  last
        msg["LUT"]=str(lut0)
        ts = dbi._timestamp()
        msg["chan"] = 0
        print (f"msg: {msg} ")

        dbi.update_lut(msg)

        
        


testdbi=test_DBI()

testdbi.test_get_lut(0)
testdbi.test_load_config()
testdbi.test_cols_vals(msg)
testdbi.test_save_calibration(msg)
testdbi.test_save_measure(msg)
testdbi.test_timestamp()
testdbi.test_list_measures()
testdbi.test_list_calibrations()
testdbi.test_update_lut_0()


    
