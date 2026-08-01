#  test_ah_meter.py:

from adc.ah_meter import AhMeter

def creates_empty():
     ah_meter = AhMeter()
     assert ah_meter.amp_sum == 0.0 , f"A bare metal creation of AhMeter should have amp_sum = {0.0}"
     assert ah_meter.start_time == 0.0 , f"A bare metal creation of AhMeter should have start_time  = {0.0}"
     assert ah_meter.vtap == 0.0 , f"A bare metal creation of AhMeter should have vtap = {0.0}"
     assert ah_meter.count == 0.0 , f"A bare metal creation of AhMeter should have count = {0.0}"
    
def test_start():
     ah_meter = AhMeter()
     start_time = time.time()
     vtap = 12.6
     ah_meter.start(start_time, vtap)
     assert ah_meter.amp_sum == 0.0, f"start(...) should have set amp_sum = {0.0}"
     assert ah_meter.count == 0, f"start(...) should have set count = {0}"
     assert ah_meter.start_time == start_time, f"start(...) should have set start_time = {start_time}"

def test_ah_used():
    ah_meter = AhMeter()
    amp_sum = 13.2
    start_time = 1785601949.0
    end_time = 1785605549.0
    vtap=12.6
    ah_meter.start(12.6, start_time)
    ah_used = ah_meter.ah_used(end_time)
    assert ah_used == 13.2, f"For given parms, ah_used should equal {13.2}"


