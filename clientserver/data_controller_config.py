# file: data_controller_config
from collections import namedtuple

#named tuples
Lut_Limits = namedtuple("Lut_Limits", ("circuit_name", "vm_low", "vb_low",
                                               "vm_high", "vb_high", "length"))


lsb = 4/pow(2,15)
circuits=["C42","C84","C126"]    # indexed by [0,1,2]
dbpath= '/Users/garth/Programming/MicroPython/usb/ryan/voltage_divider/data/db_rt'


#dummy stuff for testing:
#in future, this will be as measured by adc given input volts.
#replaced by randomized stuff in calibrate function.