# file: up/adc_cfg.py

from collections import namedtuple
from array import array
from machine import Pin, RTC, SoftI2C, PWM, Timer
import micropython
import up.ads1x15


#constants
NAMES = ["C1Cell", "C2Cells", "C3Cells", "AMPS"]
ADC_SAMPLE_RATE = micropython.const(3)               #64sps
C1Cell  = micropython.const(0)
C2Cells = micropython.const(1)
C3Cells = micropython.const(2)
AMPS    = micropython.const(3)

irq_pin = Pin(17, Pin.IN, Pin.PULL_UP)

#namedtuples
#APPS_fields:ID,OWNER, APP_DESC  ,VERSION,VERSION_DESC, TIMESTAMP  ,TEMPC,ADC_VOLT_FSR,ADC_AMP_FSR,ADC_STEPS,A2D_SZ,ADC_VOLT_MEAS_PERIOD,ADC_AMP_MEAS_PERIOD,PACK_VOLTS,RS,AMP_GAIN
Config = namedtuple("Config", ( "APP_ID", "OWNER","APP_DESC", "VERSION", "VERSION_DESC","TIMESTAMP","TEMPC","ADC_VOLT_FSR", "ADC_AMPS_FSR", "ADC_STEPS",
        "ADC_SZ", "ADC_VOLT_MEAS_PERIOD", "ADC_AMP_MEAS_PERIOD", "PACK_VOLTS", "RS", "AMP_GAIN"))  
Measurements = namedtuple("Measurements",("circuit_name", "a2d", "uclicks"))                                                                                        #5 fields

#arrays in memory for a2ds and uclicks
_BUFFERSIZE = micropython.const(64)
a2d1Cell = array("h", (0 for _ in range(_BUFFERSIZE)))
a2d2Cells = array("h", (0 for _ in range(_BUFFERSIZE)))
a2d3Cells = array("h", (0 for _ in range(_BUFFERSIZE)))
a2dAmps = array("h", (0 for _ in range(_BUFFERSIZE)))
uclicks1Cell = array("L", (0 for _ in range(_BUFFERSIZE)))
uclicks2Cells = array("L", (0 for _ in range(_BUFFERSIZE)))
uclicks3Cells = array("L", (0 for _ in range(_BUFFERSIZE)))
uclicksAmps = array("L", (0 for _ in range(_BUFFERSIZE)))
meas1Cell = Measurements(NAMES[0], a2d1Cell, uclicks1Cell)
meas2Cells= Measurements(NAMES[1], a2d2Cells, uclicks2Cells)
meas3Cells = Measurements(NAMES[2], a2d3Cells, uclicks3Cells)
measAmps = Measurements(NAMES[3], a2dAmps, uclicksAmps)
measurements= [meas1Cell, meas2Cells, meas3Cells, measAmps]


# Steps:   0.1 volt steps in 3 circuits. fetch by:  steps[C1Cell], steps[C84], steps[C126], based on 3.0-4.5 , 6.0-9.0, 9.0-13.5 V. Lengths: 16,31,46
steps1Cell = [x/10 for x in range(30,46)]
steps2Cells = [x/10 for x in range(60,91)]
steps3Cells= [x/10 for x in range(90,136)]
steps=[steps1Cell, steps2Cells, steps3Cells]

