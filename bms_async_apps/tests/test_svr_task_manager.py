#file: test_svr_task_manager.py

#  from svr.bms_asyncio_server import Server   # no need to import the server if we are not going to instantiate it.
from svr.svr_task_manager import  SvrTaskManager
from collections import OrderedDict
import math
import pytest
from copy import deepcopy

start_msg=  {'RECEIVER': 'DB', 'SENDER': 'ADC', 'TIMESTAMP': '2026-5-20  17:40:27', 'MSGID': 5010, 'CODE': 201, 'TYPE': 'c', 'CHAN': 2, 'VIN': 12.236, 'SAMP_SZ': 64, 'A2D': [21709, 21709, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24489, 24490, 24490, 24489, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24489, 24490, 24490, 24490]}
from copy import deepcopy
app_id = 1
version = 3
#svr = Server(app_id,version)     # this starts the server, do not instantiate the svr...

class FakeWriter:
    def __init__(self):
        self.data = []

    def write(self, data):
        self.data.append(data)

    async def drain(self):
        pass

@pytest.fixture
def msg():
    return  deepcopy(start_msg)

@pytest.fixture
def task_mgr():
    tm = SvrTaskManager(app_id, version)

    tm.clients = {
        "ADC": FakeWriter(),
        "GUI": FakeWriter(),
    }

    return tm

class TestSvrTaskManager:
    
    def test_compute_stats(self, task_mgr, msg):
        print("====================")
        print("\tTesting compute_stats")
        bms = task_mgr.compute_stats(msg)
        bms["MSGID"] = msg["MSGID"]
        print(f" returning bms: {bms}")
        assert bms["MSGID"] == 5010, f"Wrong msgid, should be {msg["msgid"]}"
         #TODO 2: add more compute assert statements.
        print("\tPassed compute_stats()")
    
    def test_mean(self, task_mgr, msg):
        print("====================")
        print("\tTesting mean()")
        m= task_mgr.mean([2,2,2,2])
        print(f"Mean of [2,2,2,2]  is {m}")
        assert m == 2.0, f" m is not the mean is should be {2.0} "
        print("\tPassed test_mean()")
        
    def test_lookup_chan_vm(self, task_mgr):
        print("====================")
        print("\tTesting lookup_chan_vm()")
        vm=3.1
        chan=2
        vb = task_mgr.lookup_chan_vm( chan, vm)
        print(f" Looked up value of vb on chan {chan} when vm is {vm} is:  {vb}")
        #TODO 1: add lookup assert statements.
         
        print("\tPassed test_lookup_chan_vm()")
    
    @pytest.mark.asyncio
    async def test_adc_measure(self, task_mgr, msg):
        await task_mgr.send_to_client("ADC", msg, task_mgr.clients)
        print(f" msg: {msg}")
        print(f" clients: {task_mgr.clients}")
    
    @pytest.mark.asyncio
    async def test_adc_calibrate(self, task_mgr, msg):
        await task_mgr.send_to_client("ADC", msg, task_mgr.clients)
        print(f" msg: {msg}")

    @pytest.mark.parametrize(
                "code,arglist",
        [
          pytest.param(302, [], id="302-sync_time"),
          pytest.param(304, [], id="304-max-meas-id"),
          pytest.param(310, [], id="310-get_app_config" ),
          pytest.param(312, [0], id="312-get_chan_config" ),
          pytest.param(330, [0, "m"], id="330-list-chan0-measure"),
          pytest.param(330, [0, "c"], id="330-list-chan0-calibrate"),
          pytest.param(340, [5], id="340-get_bms_a2d_samples"),
          pytest.param(350, [0], id="350-get_lut"),
          pytest.param(390, [], id="390-get_estimator_parms"),
        ],
    )
    def test_call_function(self, code, arglist,task_mgr,  msg):
        task_mgr.dbi.call_function(code, arglist)

# ======= delete of comment out everything below this line==========        
"""    
tmp =  TestSvrTaskManager(1,3)
tmp.test_compute_stats()
tmp.test_mean()
tmp.test_lookup_chan_vm()
tmp.test_call_function(101, [], msg)
tmp.test_adc_measure(msg)
tmp.test_adc_calibrate(msg)
 list of functions in SvrTaskManager:
    def __init__(self, app_id, version):      # removed , svr from argslist
    def load_functions_dict(self):
    def get_app_config(self):
    def get_chan_config(self, chan):
    def adc_setup_periodic(self, functions_dict, argslist):
    def load_luts(self):
    def get_estimator_parms(self):
    async def send_to_client(self, name, msg, clients):
    async def adc_calibrate(self):
    async def adc_measure(self):
    def predict_vb(self, chan):
    def test_reportability(self, vb):
    async def create_and_schedule_tasks (self, loop, msg, clients ):
    def compute_stats(self, msg):
           "DISCARD_SZ", "KEEP_SZ  embedded. The entire BMS namedtuple is defined in
    def lookup_chan_vm(self,  chan:int, vm:float):
            # vm was outside of allowable bounds... so vb is undefined...
    def mean(self, alist):
    def matchesboundary(self, chan:int, vm:float, version:int) :
"""
    
    
    
