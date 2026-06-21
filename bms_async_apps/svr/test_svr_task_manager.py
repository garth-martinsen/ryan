#file: test_svr_task_manager.py

from bms_asyncio_server import Server
from svr_task_manager import  SvrTaskManager
from collections import OrderedDict
import math

msg=  {'RECEIVER': 'DB', 'SENDER': 'ADC', 'TIMESTAMPS': '2026-5-20  17:40:27', 'MSGID': 5010, 'CODE': 201, 'TYPE': 'c', 'CHAN': 2, 'VIN': 12.236, 'SAMP_SZ': 64, 'SAMPLES': [21709, 21709, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24489, 24490, 24490, 24489, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24489, 24490, 24490, 24490]}
app_id = 1
version = 3
svr = Server(app_id,version)


class TestSvrTaskManager:
    def __init__(self, app_id, version, svr):
        self.task_mgr =  SvrTaskManager(app_id, version)
    
    def test_compute_stats(self):
        print("====================")
        print("\tTesting compute_stats")
        bms = self.task_mgr.compute_stats(msg)
        print(f" returning bms: {bms}")
        assert bms.MSGID == 5010, f"Wrong msgid, should be {msg["msgid"]}"
         #TODO 2: add more compute assert statements.
        print("\tPassed compute_stats()")
    
    def test_mean(self):
        print("====================")
        print("\tTesting mean()")
        m= self.task_mgr.mean([2,2,2,2])
        print(f"Mean of [2,2,2,2]  is {m}")
        assert m == 2.0, f" m is not the mean is should be {2.0} "
        print("\tPassed test_mean()")
        
    def test_lookup_chan_vm(self):
        print("====================")
        print("\tTesting lookup_chan_vm()")
        vm=3.1
        chan=2
        vb = self.task_mgr.lookup_chan_vm( chan, vm)
        print(f" Looked up value of vb on chan {chan} when vm is {vm} is:  {vb}")
        print(f"\tNote: computing vb= vm/vd_fract gives vb: {vm/self.task_mgr.vd_fracts[chan]}")
        #TODO 1: add lookup assert statements.
        print("\tPassed test_lookup_chan_vm()")
    
    def test_adc_measure(self, msg):
        print(f" msg: {msg}")
        print(f" clients: {self.task_mgr.clients}")
        self.task_mgr.send_to_client ("ADC", msg, self.task_mgr.clients)
      
    def test_adc_calibrate(self, msg):
        print(f" msg: {msg}")
        self.task_mgr.send_to_client ("ADC", msg, self.task_mgr.clients)
  
    async def test_call_function(self, code, argslist, msg):
        await self.task_mgr.call_function(code, argslist, msg)
        
    
tmp =  TestSvrTaskManager(1,3)
tmp.test_compute_stats()
tmp.test_mean()
tmp.test_lookup_chan_vm()
tmp.test_call_function(101, [], msg)
tmp.test_adc_measure(msg)
tmp.test_adc_calibrate(msg)

    
    
    