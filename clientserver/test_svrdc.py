# file test_svrdc.py  Given a msg, call dbi to save the bms in the msg to BMS table in database rt_db.

from async_svr_data_controller import AsyncSvrDataController
import socket

msg1={"purpose":101, "chan": 0,  "cfg_id": 1, "a2d":   27594.82, "timestamp": "2025-8-9  17:3:57.162999", "a2d_sd": 1.249841, "vin": -99,      "error": 0.002,             "vm": 3.448513, "vb": 3.788,         "store_time": 0.000448, "gate_time": 1.00018,  "sample_period": 0.015625, "keep": [27585, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595]}
msg2={"purpose":201, "chan": 0,  "cfg_id": 1, "a2d":  27594.84,  "timestamp": "2025-8-9  17:3:57.162999", "a2d_sd": 1.249841,  "vin": 3.805, "error": -0.01989841, "vm": 3.448513, "vb": 3.785102, "store_time": 0.000448, "gate_time": 1.00018,  "sample_period": 0.0156,      "keep": [27585, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595, 27595]}

   #  BMS:  "id", "cfg_id","type",  "timestamp", "a2d_mean",  "a2d_sd",  "vm",  "vb",  "vin",  "error",  "keep",  "sample_period",  "store_time",  "gate_time",
     
sockets: dict[str, socket]={}
cfg_ids=(1,2,3)

class test_DC:
    def __init__(self):
        self.dc = AsyncSvrDataController(cfg_ids, sockets)
       # self.dc.load_configscfg_ids)
     
    def test_constructor(self):
        print("===================")
        print("testing constructor for dc.cfg")
        print(f" dc.cfg_ids: {self.dc.cfg_ids}")
        assert self.dc.cfg_ids == (1,2,3)
        #print(f" lut0 : {self.dc.luts[0]}  luts1: {self.dc.luts[1]} luts2: {self.dc.luts[2]}")
        print(" Test luts for correct sizes")
        assert len(self.dc.luts[0]) > 15, 'Lut0 is not loaded'
        assert len(self.dc.luts[1]) > 30, 'Lut1 is not loaded'
        assert len(self.dc.luts[2]) > 45, 'Lut2 is not loaded'
        
        
        return ("======== pass =======")


    #save_measurement(self, msg):
    def test_save_measurement(self):
        '''        '''
        print("===================")
        print("testing dc.save_measurement(msg)")
        msg=msg1
        chan = msg['chan']
        msg['purpose']=101   # add back in for test
        msg['sender_id']="adc_client"   # add back in for test
        msg['msg_id']= 1234   # add back in for test
        ts=self.dc.dbi.timestamp()
        msg["timestamp"]= ts
        
        self.dc.dbi.save_measurement(msg)                     #method under test: mut
        records = self.dc.dbi.list_measurements(chan)       #pull records from db to verify
        print(f" records pulled: {len(records)}")
        last = records[-1]                                               # last record
        print(" Testing type and timestamp:")
        assert last[2]=='m', "Wrong type"
        assert last[3]== ts, f"Timestamp is wrong: {ts} is not {last[3]}"
        return ("======== pass =======")

    def test_save_calibration(self):
        print("===================")
        print("testing dc.save_calibration(msg)")
        msg=msg2
        msg['purpose']='201'
        msg['type']='c'
        msg['purpose']=101   # add back in for test
        msg['sender_id']="adc_client"   # add back in for test
        msg['msg_id']= 1234   # add back in for test
        ts =  ts=self.dc.dbi.timestamp()
        msg["timestamp"]= ts
        self.dc.dbi.save_calibration(msg)
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
        #assert len(luts[1]) > 30
        #assert len(luts[2]) > 44
        return ("======== pass =======")


testdc= test_DC()

print(testdc.test_constructor())
print(testdc.test_save_measurement())
print(testdc.test_save_calibration())
print(testdc.test_lut_files())
