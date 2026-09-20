# file: adc/mp_fixtures.py

from common.bms_config import APP_ID, VERSION
from copy import deepcopy
import adc
from adc_cfg import ADC_TO_SVR_TEMPLATE

 # mpremote will not cp into deep hierarchies , so flatten the following by copy/paste:
adc_fields_bms = {"APP_ID", "VERSION", "MSGID", "TIMESTAMP","TYPE", "CHAN", "VIN", "SAMP_SZ", "MEAS_ID"}
adc_fields_amp_hrs = {"MEAS_ID", "TIMESTAMP", "I_MEAN", "PERIOD_SEC", "AH_USED"}
adc_rqd_fields = adc_fields_bms | adc_fields_amp_hrs

MEAN_A2D_BY_CHAN = (24558, 19394, 22326)
OFFSETS = (-1, 0, 0, 0)

#The app to be tested...
def adc_fixture():
    """Return the ADC object used by the hardware tests."""
    return adc.ADC(APP_ID, VERSION)

# the fields for which  the adc must provide values
def adc_rqd_fields_fixture():
    """Return a fresh copy of the required ADC fields."""
    return deepcopy(adc_rqd_fields)

# the report template which the app will populate. It will be tested against expected values.
def report_fixture():
    """Return a fresh report template."""
    return deepcopy(ADC_TO_SVR_TEMPLATE)

# the expected report filled with expected values. It will be tested against populated report values.
def expected_report_fixture():
    """Return a fresh report template. It will be modified in the test method."""
    return deepcopy(ADC_TO_SVR_TEMPLATE)

def vins_fixture():
    """Return the three test input voltages."""
    return [4.0, 8.0, 12.0]

def make_a2d_samples(mean_a2d):
    """Return 64 deterministic samples within one count of the mean."""
    a2d = []
    for index in range(64):
        a2d.append(mean_a2d + OFFSETS[index % len(OFFSETS)])
    return a2d

def a2d_fixture():
    """Return one fresh 64-sample list for each voltage channel."""
    return [
        make_a2d_samples(mean_a2d)
        for mean_a2d in MEAN_A2D_BY_CHAN
]

def amps_chan_fixture():
    """chan 3, I_MEAN, PERIOD_SEC, AH_USED"""
    return [3, 0.87, 3600, 0.87]
