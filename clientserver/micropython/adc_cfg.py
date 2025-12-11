# file: adc_cfg.py

from collections import namedtuple
from array import array
from machine import Pin, RTC, SoftI2C, PWM, Timer
import micropython
import ads1x15

#constants
ssid = 'Ziply1824'
password = "1408945739"
names = ["C42", "C84", "C126"]
adc_address =micropython.const(72)
adc_sample_rate = micropython.const(3)               #64sps
adc_gain = micropython.const(0)                            # max voltage= 6.144 V for chan 0, else will be set by channel
C42=micropython.const(0)
C84=micropython.const(1)
C126=micropython.const(2)

#pins   6 pins
gate_42=Pin(25, Pin.OUT, Pin.PULL_UP)
gate_84=Pin(26, Pin.OUT, Pin.PULL_UP)
gate_126=Pin(27, Pin.OUT, Pin.PULL_UP)
scl=Pin(22)
sda=Pin(21)
irq_pin = Pin(17, Pin.IN, Pin.PULL_UP)

#namedtuples
Config = namedtuple("Config", ( "cfg_id", "owner", "app_id", "app_desc", "chan_id","chan_desc", "version_id", "version_desc",
        "creation_time", "mosfet", "mosfet_type", "tempC", "ADC_GAIN", "ADC_SAMPLE_RATE", "r1", "r2", "rp", "rg", "LUT_CALIBRATED","LUT" ))  
Measurements = namedtuple("Measurements",("circuit_name", "a2d", "uclicks"))                                                                                        #5 fields
Stats = namedtuple("Stats", ("circuit_name",  "vin", "sample_sz","a2d_mean", "vm_mean", "sd", "sample_period","store_time","gate_time"))                                                                                           #9 fields
BMS = namedtuple("BMS", ('timestamp', 'type', 'chan',  'cfg_id', 'a2d',  'a2d_sd', 'sample_sz',  'vin','vm', 'vb',  'error', 'store_time', 'gate_time', 'sample_period',  'keep')  )   #15 fields
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

# Steps:   0.1 volt steps in 3 circuits. fetch by:  steps[C42], steps[C84], steps[C126], based on 3.0-4.5 , 6.0-9.0, 9.0-13.5 V. Lengths: 16,31,46
steps42 = [x/10 for x in range(30,46)]
steps84 = [x/10 for x in range(60,91)]
steps126= [x/10 for x in range(90,136)]
steps=[steps42, steps84, steps126]

# exports: names, i2c, ads, Measurements, Stats, Record, measurements, allPins, gatePins, steps
