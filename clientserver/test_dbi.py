# file test_dbi.py  Given a msg, save the bms in the msg to BMS table in database rt_db.

from database_interface import DatabaseInterface
msg={"purpose":201, "store_time": 0.000448, "gate_time": 1.00018, "cfg_id": 1, "a2d": 27594.84, "sample_sz": 44, "timestamp": "2025-8-9  17:3:57.162999", "a2d_sd": 1.249841, "purpose": 201, "vin": 3.805, "error": -0.01989841, "vm": 3.448513, "vb": 3.785102, "keep": [27585, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595], "sample_period": 0.015625}
dbi = DatabaseInterface((1,2,3))

class test_DBI:
    
    def test_cols_vals(self, msg):
        print("===================")
        print("testing create_cols_vals()")
        ts= dbi.timestamp()
        msg['timestamp']=ts
        msg["sender_id"]="adc_client"
        msg["msg_id"]=1234
        msg["chan"]=0
        cols, vals = dbi.create_cols_vals(msg)
        #print(f" cols: {cols}  vals: {vals}")
        assert len(cols) == len(vals), "Cols and Vals must have same length"
        print("Passed")
        
    def test_timestamp(self):
        print("===================")
        print("testing timestamp()")
        ts= dbi.timestamp()
        print(f"timestamp: {ts}")
        records = dbi.list_calibrations()
        last=records[-1]
        assert last[3][:-3] == ts[:-3], f" Timestamp is incorrect! {ts} from last record:{last[3]}" 
        print("Passed")

    def test_save_calibration(self, msg):
        print("===================")
        print("testing save_calibration()")
        msg['purpose']=201   # add back in for test
        msg["chan"]=0            # add back in for test
        msg["sender_id"]="adc"           # add back in for test
        msg["msg_id"]=1234    # add back in for test
        #msg.pop("sample_sz")
        ts= dbi.timestamp()
        msg['timestamp']=ts
        msg['type']='c'
        #save to db
        dbi.save_calibration(msg)
        #read from db
        records = dbi.list_calibrations()
        print(f" len(records) : {len(records)}")
        last_record = records[-1]
        print(f" Last Record : {last_record}")
        print(f" vm: {last_record[6]}")
        assert last_record[2] == 'c' , f" Wrong type: {last_record[2]} is not 'c'"
        assert last_record[7]==msg["vm"], f"Vm is different from input to saved record {last_record[7]}"
        assert ts == last_record[3] , f" Timestamp of record: {last_record[2]} differs from ts {ts}"
        print("Passed")

    def test_save_measure(self,msg):
        print("===================")
        print("testing save_measure()")
        chan=0
        msg['purpose']=201   # add back in for test
        msg['sender_id']="adc_client"   # add back in for test
        msg['msg_id']="adc_client"   # add back in for test
        msg["chan"]=0            # add back in for test
        ts= dbi.timestamp()
        msg['timestamp']=ts
        msg['type']='test_calibrate.py'
        # save to db
        dbi.save_measurement(msg)
        # read from db
        records = dbi.list_measurements(chan)
        print(f" len(records) {len(records)}")
        last_record = records[-1]
        # print(f" Last Record : {last_record}")
        assert last_record[2] == 'm' , f" Type: {last_record[2]} should be 'm'"
        assert last_record[7]==msg["vm"], f" Vm: {last_record[6]} is not {msg['vm']}"
        assert last_record[3] == ts, f" Timestamp is wrong.  {last_record[2]} differs from ts : {ts}"
        print( "Passed")

    def test_list_calibrations(self,msg):
        print("===================")
        print("testing list_calibrations()")
        records = dbi.list_calibrations()
        last_record = records[-1]
        #print(f" records[-1]: {records[-1]}")
        assert last_record[2] == 'c' , f" Type: {last_record[2]} is not 'c'"
        print("Passed")


testdbi=test_DBI()

testdbi.test_cols_vals(msg)
testdbi.test_save_calibration(msg)
testdbi.test_save_measure(msg)
testdbi.test_timestamp()

    
