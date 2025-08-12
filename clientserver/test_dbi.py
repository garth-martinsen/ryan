# file test_dbi.py  Given a msg, save the bms in the msg to BMS table in database rt_db.

from database_interface import DatabaseInterface
msg={"purpose":201, "store_time": 0.000448, "gate_time": 1.00018, "cfg_id": 1, "a2d": 27594.84, "timestamp": "2025-8-9  17:3:57.162999", "a2d_sd": 1.249841, "purpose": 201, "vin": 3.805, "error": -0.01989841, "vm": 3.448513, "vb": 3.785102, "keep": [27585, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595], "sample_period": 0.015625}
dbi = DatabaseInterface()

class test_DBI:
    
    def test_cols_vals(self, msg):
        print("===================")
        print("testing create_cols_vals()")
        ts= dbi.timestamp()
        msg['timestamp']=ts
        cols, vals = dbi.create_cols_vals(msg)
        print(f" cols: {cols}  vals: {vals}")
        assert(len(cols) == len(vals), "Cols and Vals must have same length")
        
    def test_timestamp(self):
        print("===================")
        print("testing timestamp()")
        ts= dbi.timestamp()
        print(f"timestamp: {ts}")
        records = dbi.list_BMS()
        last=records[-1]
        assert(last["timestamp"] == ts, " Timestamp is incorrect!")
        
    def test_save_calibration(self, msg):
        print("===================")
        print("testing save_calibration()")
        msg['purpose']=201   # add back in for test
        ts= dbi.timestamp()
        msg['timestamp']=ts
        msg['type']='c'
        #save to db
        dbi.save_calibration(msg)
        #read from db
        records = dbi.list_BMS()
        last_record = Record: {records[-1]
        print(f" Last Record : {last_record}")
        assert(last_record["type"] == 'c' )
        assert(last_record["vm"]==msg["vm"], "Vm is different from input to saved record")
        
    def test_save_measure(self,msg):
        print("===================")
        print("testing save_measure()")
        msg['purpose']=201   # add back in for test
        ts= dbi.timestamp()
        msg['timestamp']=ts
        msg['type']='test_calibrate.py'
        # save to db
        dbi.save_measurement(msg)
        # read from db
        records = dbi.list_BMS()
        last_record = Record: {records[-1]
        print(f" Last Record : {last_record}")
        assert(last_record["type"] == 'm' )
        assert(last_record["vm"]==msg["vm"], "Vm is different from input to saved record")
        

 
testdbi=test_DBI()

testdbi.test_cols_vals(msg)
testdbi.test_save_calibration(msg)
testdbi.test_timestamp()
testdbi.test_save_measure(msg)

    
