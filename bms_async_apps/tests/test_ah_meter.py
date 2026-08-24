#  test_ah_meter.py:
import time
from adc.ah_meter import AhMeter
import pytest

#Test Data fields.
VTAP=12.6
LSB = 31.25E-6
RS = 0.05
AMP_GAIN = 20
A2D = [17601, 17601, 17599, 17600, 17601, 17601, 17599, 17599, 17599, 17600, 17600, 17599, 17600, 17599, 17600, 17599, 17601, 17601, 17600, 17599, 17601, 17600, 17600, 17599, 17601, 17601, 17600, 17599, 17599, 17599, 17600, 17600, 17599, 17600, 17601, 17600, 17601, 17599, 17599, 17599, 17599, 17599, 17600, 17600, 17600, 17600, 17601, 17599, 17599, 17599, 17600, 17601, 17599, 17600, 17601, 17601, 17601, 17600, 17601, 17599, 17599, 17600, 17601, 17599, 17599]
START_TIME =  1785609149.00
END_TIME   = 1785612749.0

def creates_empty():
    #  'vtap', 'lsb', 'rs', 'amp_gain', and 'a2d
    global VTAP, LSB, RS, AMP_GAIN, A2D
    ah_meter = AhMeter(VTAP,LSB,RS,AMP_GAIN,A2D)
    assert ah_meter.amp_sum == 0.0 , f"A bare metal creation of AhMeter should have amp_sum = {0.0}"
    assert ah_meter.start_time == 0.0 , f"A bare metal creation of AhMeter should have start_time  = {0.0}"
    assert ah_meter.count == 0.0 , f"A bare metal creation of AhMeter should have count = {0.0}"
    
def test_start():
    global VTAP, LSB, RS, AMP_GAIN, A2D
    ah_meter = AhMeter(VTAP,LSB,RS,AMP_GAIN,A2D)
    vtap = 12.6
    ah_meter.start(START_TIME )
    assert ah_meter.amp_sum == 0.0, f"start(...) should have set amp_sum = {0.0}"
    assert ah_meter.count == 0, f"start(...) should have set count = {0}"
    assert ah_meter.start_time == START_TIME, f"start(...) should have set start_time = {start_time}"

def test_ah_used():
    global VTAP, LSB, RS, AMP_GAIN, A2D
    ah_meter = AhMeter(VTAP,LSB,RS,AMP_GAIN,A2D)
    ah_meter.start_time =  START_TIME
    ah_meter.end_time =  END_TIME
    ah_meter.amp_sum = 13.2
    ah_meter.count=60
    # run tested method
    ah_used = ah_meter.ah_used()
    # assert on results
    assert ah_used == .22, f"For given parms, ah_used should equal {13.2/60*1}"

