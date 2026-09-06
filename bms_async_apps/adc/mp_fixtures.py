# file: adc/mp_fixtures.py

import adc

#from common.rqd_fields import adc_fields_bms
#from common.templates.adc_templates import ADC_TO_SVR_TEMPLATE
from copy import deepcopy

# mpremote will not cp into deep hierarchies , so to replace first two imports...
#to flatten out imports ADC_TO_SVR_TEMPLATE is copy pasted into mp_fixtures.py
ADC_TO_SVR_TEMPLATE = { "SENDER":"ADC", "RECEIVER":"SVR", "APP_ID":1, "VERSION":3, "CODE": 101, "MSGID": 123, "MEAS_ID":1, "TYPE":"m", "CHANS":[ 
   {"CHAN":0, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #A2D will have 64 values.. just dummy here... 
   {"CHAN":1, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #likewise
   {"CHAN":2, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #likewise
   {"CHAN":3, "TIMESTAMP": 178000.0, "I_MEAN":0.550,"PERIOD_SEC":3600, "AH_USED":0.550 } # values will vary but no arrays...
 ] }

#to flatten out imports, rqd_fields is copy pasted into mp_fixtures.py
adc_fields_bms = {"APP_ID", "VERSION", "MSGID", "TIMESTAMP","TYPE", "CHAN", "VIN", "SAMP_SZ", "MEAS_ID"}
adc_fields_amp_hrs = {"MEAS_ID", "TIMESTAMP", "I_MEAN", "ELAPSED_SEC", "AH_USED"}
adc_rqd_fields = adc_field_bms | adc_fields_amp_hrs

MEAN_A2D_BY_CHAN = (24558, 19394, 22326)
OFFSETS = (-1, 0, 1, 0)


def adc_fixture():
    """Return the ADC object used by the hardware tests."""
    return adc.ADC()

def adc_rqd_fields_fixture():
    """Return a fresh copy of the required ADC fields."""
    return deepcopy(adc_fields_bms)

def report_fixture():
    """Return a fresh report template."""
    return deepcopy(ADC_TO_SVR_TEMPLATE)

def vins_fixture():
    """Return the three test input voltages."""
    return [4.0, 8.0, 12.0]

def make_a2d_samples(mean_a2d):
    """Return 64 deterministic samples within one count of the mean."""
    return [
        mean_a2d + OFFSETS[index % len(OFFSETS)]
        for index in range(64)
    ]

def a2d_fixture():
    """Return one fresh 64-sample list for each voltage channel."""
    return [
        make_a2d_samples(mean_a2d)
        for mean_a2d in MEAN_A2D_BY_CHAN
]

def amps_fixture():
    """chan 3, I_MEAN, PERIOD_SEC, AH_USED"""
    return [3, 0.87, 3600, 0.87]
