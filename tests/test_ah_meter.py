#  test_ah_meter.py:
import time
from tests.test_data.ah_meter_test_data import START_TIME, END_TIME, VTAP, AMP_SUM, COUNT
from adc.ah_meter import AhMeter
import pytest

@pytest.fixture
def a2d():
    return [17601, 17601, 17599, 17600, 17601, 17601, 17599, 17599, 17599, 17600, 17600, 17599, 17600, 17599, 17600, 17599, 17601, 17601, 17600, 17599, 17601, 17600, 17600, 17599, 17601, 17601, 17600, 17599, 17599, 17599, 17600, 17600, 17599, 17600, 17601, 17600, 17601, 17599, 17599, 17599, 17599, 17599, 17600, 17600, 17600, 17600, 17601, 17599, 17599, 17599, 17600, 17601, 17599, 17600, 17601, 17601, 17601, 17600, 17601, 17599, 17599, 17600, 17601, 17599, 17599]

def test_creates_empty():
     ah_meter = AhMeter(VTAP,31.25E-6, 0.05, 20,a2d)
     assert ah_meter.amp_sum == 0.0 , f"A bare metal creation of AhMeter should have amp_sum = {0.0}"
     assert ah_meter.start_time == 0.0 , f"A bare metal creation of AhMeter should have start_time  = {0.0}"
     assert ah_meter.vtap == VTAP , f"A bare metal creation of AhMeter should have correct vtap = {VTAP}"
     assert ah_meter.count == 0.0 , f"A bare metal creation of AhMeter should have count = {0.0}"
    
def test_start():
     #self, vtap, lsb, rs, amp_gain
     ah_meter = AhMeter(VTAP,31.25E-6, 0.05, 20,a2d)
     start_time = START_TIME   
     vtap = VTAP
     ah_meter.start(start_time )
     assert ah_meter.amp_sum == 0.0, f"start(...) should have set amp_sum = {0.0}"
     assert ah_meter.count == 0, f"start(...) should have set count = {0}"
     assert ah_meter.start_time == start_time, f"start(...) should have set start_time = {start_time}"

def test_ah_used():
    ah_meter = AhMeter(VTAP,31.25E-6, 0.05, 20,a2d)
    start_time = START_TIME
    end_time   = END_TIME

    vtap=VTAP
    ah_meter.start(start_time)
    ah_meter.end_time=end_time
    ah_meter.amp_sum = AMP_SUM
    ah_meter.count=COUNT
    ah_used = ah_meter.ah_used()

    assert ah_used == .22, f"For given parms, ah_used should equal {13.2/60*1}"
#=========delete below this line==========
'''
#start_time:time.localtime(1785601949.0)=time.struct_time(tm_year=2026,tm_mon=8,tm_mday=1,tm_hour=9,tm_min=32,tm_sec=29,tm_wday=5, tm_yday=213, tm_isdst=1)
START_TIME = 1785609149.00
#start_time:time.localtime(1785601949.0)=time.struct_time(tm_year=2026,tm_mon=8,tm_mday=1,tm_hour=10,tm_min=32,tm_sec=29,tm_wday=5, tm_yday=213, tm_isdst=1)
END_TIME = 1785612749.0
# Fully charged ...
VTAP = 12.6
# Mocked amp_sum, count
AMP_SUM = 13.2
COUNT = 60
'''


