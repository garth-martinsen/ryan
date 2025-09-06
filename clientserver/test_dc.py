# file test_dc.py  Given a msg, call dbi to save the bms in the msg to BMS table in database rt_db.

from data_controller import DataController
msg1={"purpose":101, "chan": 0, "store_time": 0.000443, "gate_time": 1.0012, "cfg_id": 1, "a2d":   27594.82, "timestamp": "2025-8-9  17:3:57.162999", "a2d_sd": 1.249841, "purpose": 101, "vin": -99, "error": 0.002, "vm": 3.448513, "vb": 3.788, "keep": [27585, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595], "sample_period": 0.015625}
msg2={"purpose":201, "chan": 0, "store_time": 0.000448, "gate_time": 1.00018, "cfg_id": 1, "a2d": 27594.84, "timestamp": "2025-8-9  17:3:57.162999", "a2d_sd": 1.249841, "purpose": 201, "vin": 3.805, "error": -0.01989841, "vm": 3.448513, "vb": 3.785102, "keep": [27585, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595], "sample_period": 0.015625}


class test_DC:
    def __init__(self):
        self.dc = DataController((1,2,3))
     
    def test_constructor(self):
        print("===================")
        print("testing constructor for dc.cfg")
        print(f" dc.cfg_ids: {self.dc.cfg_ids}")
        assert self.dc.cfg_ids == (1,2,3)
        assert len(self.dc.luts[0]) > 14, 'Lut0 is not loaded'
        assert len(self.dc.luts[1]) > 30, 'Lut0 is not loaded'
        assert len(self.dc.luts[2]) > 44, 'Lut0 is not loaded'
        
        
        return ("======== pass =======")


    #save_measurement(self, msg):
    def test_save_measurement(self):
        '''        '''
        print("===================")
        print("testing dc.save_measurement(msg)")
        msg=msg1
        chan = msg['chan']
        #msg['purpose']='100'
        ts=self.dc.dbi.timestamp()
        msg["timestamp"]= ts
        self.dc.save_measurement(msg)                     #method under test: mut
        records = self.dc.dbi.list_measurements()       #pull records from db to verify
        last = records[-1]                                               # last record
        #print(f" last record: {last} ")
        assert last[2]=='m', "Wrong type"
        assert last[3]== ts, f"Timestamp is wrong: {ts} is not {last[3]}"
        return ("======== pass =======")

    def test_save_calibration(self):
        print("===================")
        print("testing dc.save_calibration(msg)")
        msg=msg2
        msg['purpose']='201'
        msg['type']='c'
        ts =  ts=self.dc.dbi.timestamp()
        msg["timestamp"]= ts
        self.dc.save_calibration(msg)
        records = self.dc.dbi.list_calibrations()
        last=records[-1]
        #print(f" last record: {last} ")
        assert last[2]=='c', f"Wrong type. Should be {'c'}"
        assert last[3]==ts, "Timestamp is wrong"
        return ("======== pass =======")
    
    def test_lut_files(self):
        print("===================")
        print("testing dc.luts")
        luts = self.dc.luts
        #print(f" luts[0] : {luts[0]}")
        #print(f" luts[1] : {luts[1]}")
        #print(f" luts[2] : {luts[2]}")
        print(f"len lut0: { len(luts[0])}")
        print(f"len lut1: { len(luts[1])}")
        print(f"len lut2: { len(luts[2])}")
        assert len(luts[0]) > 14
        assert len(luts[1]) > 30
        assert len(luts[2]) > 44
        return ("======== pass =======")


testdc= test_DC()

print(testdc.test_constructor())
print(testdc.test_save_measurement())
print(testdc.test_save_calibration())
print(testdc.test_lut_files())