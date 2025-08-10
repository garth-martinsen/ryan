# file: adc_cfg.py

from collections import namedtuple
from array import array
from machine import Pin, RTC, SoftI2C, PWM, Timer
import micropython
import ads1x15

#constants
PATH = '//Users/garth/Programming/MicroPython/usb/ryan/voltage_divider/scripts/rpvdclass.py'
ssid = 'Ziply1824'
password = "1408945739"
names = ["C42", "C84", "C126"]
adc_address =micropython.const(72)
adc_sample_rate = micropython.const(3) #64sps
adc_gain = micropython.const(1)  # max voltage= 4.095V
C42=micropython.const(0)
C84=micropython.const(1)
C126=micropython.const(2)

#pins
gate_42=Pin(25, Pin.OUT, Pin.PULL_UP)
gate_84=Pin(26, Pin.OUT, Pin.PULL_UP)
gate_126=Pin(27, Pin.OUT, Pin.PULL_UP)
scl=Pin(22)
sda=Pin(21)
irq_pin = Pin(17, Pin.IN, Pin.PULL_UP)

#namedtuples
Measurements = namedtuple("Measurements",("circuit_name", "a2d", "uclicks"))                                                                                        #5 fields
Stats = namedtuple("Stats", ("circuit_name",  "vin", "a2d_mean", "vm_mean", "sd", "sample_period","store_time","gate_time"))                                                                                           #9 fields
SvrReport = namedtuple("SvrReport", ("datetime", "circuit_name",  "cfg_id", "chan", "vm", "vm_sd", "Vb", "sample_period","store_time","gate_time")  )            # 10 fields
GatePins = namedtuple("GatePins",("C_42", "C_84", "C_126"))
AllPins = namedtuple("AllPins",("gate_42", "gate_84", "gate_126", "sda", "scl", "alert"))

gatePins = [gate_42, gate_84, gate_126]
allPins = AllPins(gate_42,gate_84,gate_126, sda, scl, irq_pin)
#arrays in flash memory for a2ds and uclicks
_BUFFERSIZE = micropython.const(64)
a2d42 = array("h", (0 for _ in range(_BUFFERSIZE)))
a2d84 = array("h", (0 for _ in range(_BUFFERSIZE)))
a2d126 = array("h", (0 for _ in range(_BUFFERSIZE)))
uclicks42 = array("L", (0 for _ in range(_BUFFERSIZE)))
uclicks84 = array("L", (0 for _ in range(_BUFFERSIZE)))
uclicks126 = array("L", (0 for _ in range(_BUFFERSIZE)))
meas42= Measurements(names[0], a2d42, uclicks42)
meas84= Measurements(names[1], a2d84, uclicks84)
meas126 = Measurements(names[2], a2d126, uclicks126)
measurements= [meas42, meas84, meas126]
#i2c and ads
i2c= SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000)
ads=ads1x15.ADS1115(i2c, adc_address, adc_gain)    # ADC sampler

# exports: names, i2c, ads, Measurements, Stats, Record, measurements, allPins, gatePins
