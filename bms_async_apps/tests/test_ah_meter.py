#  test_ah_meter.py:
import time

from adc.ah_meter import AhMeter

def creates_empty():
     ah_meter = AhMeter()
     assert ah_meter.amp_sum == 0.0 , f"A bare metal creation of AhMeter should have amp_sum = {0.0}"
     assert ah_meter.start_time == 0.0 , f"A bare metal creation of AhMeter should have start_time  = {0.0}"
     assert ah_meter.vtap == 0.0 , f"A bare metal creation of AhMeter should have vtap = {0.0}"
     assert ah_meter.count == 0.0 , f"A bare metal creation of AhMeter should have count = {0.0}"
    
def test_start():
     ah_meter = AhMeter()
     start_time = 1785609149.00   #time.localtime(1785601949.0)= time.struct_time(tm_year=2026, tm_mon=8, tm_mday=1, tm_hour=9, tm_min=32, tm_sec=29, tm_wday=5, tm_yday=213, tm_isdst=1)
     vtap = 12.6
     ah_meter.start(vtap, start_time )
     assert ah_meter.amp_sum == 0.0, f"start(...) should have set amp_sum = {0.0}"
     assert ah_meter.count == 0, f"start(...) should have set count = {0}"
     assert ah_meter.start_time == start_time, f"start(...) should have set start_time = {start_time}"

def test_ah_used():
    ah_meter = AhMeter()
    start_time = 1785609149.0
    end_time   = 1785612749.0
    vtap=12.6
    ah_meter.start(vtap, start_time)
    ah_meter.amp_sum = 13.2
    ah_meter.count=60
    ah_used = ah_meter.ah_used(end_time)

    assert ah_used == .22, f"For given parms, ah_used should equal {13.2/60*1}"


