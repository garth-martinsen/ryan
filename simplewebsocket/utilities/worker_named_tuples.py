# file worker_named_tuples.py

from collections import namedtuple

Config_fields = ["ID","OWNER","APP_ID","APP_DESC","CHAN","CHANNEL_DESC","VERSION_ID","VERSION_DESC","TIMESTAMP","TEMPC","ADC_FSR","ADC_SAMPLE_RATE","C1","R1","R2","LUT_CALIBRATED","LUT_TS","VD_FRACT","ADC_BITS"]
Config = namedtuple("Config", Config_fields)
cfg1= Config( 1 , "GM" , 1 , "Development", 0 , " 3-4.5V circuit chan(0)", 1 , " BASELINE VERSION", " 2026-3-16_9:8:42", 25.4 , 1 , 3, 1.0e-07, 99300.0, 219100.0, 0 ," 2026-3-22_16:45:17", 0.688128140703518, 15 )

Config_fields2 = [ "ID" , "OWNER" , "APP_ID" , "APP_DESC" , "CHAN" , "CHANNEL_DESC" , "VERSION_ID" ,"VERSION_DESC" , "TIMESTAMP" , "TEMPC" , "ADC_FSR" , "ADC_STEPS" , "ADC_SAMPLE_RATE" , "C1" , "R1" , "R2" , "VD_FRACT" , "LUT_CALIBRATED" , "LUT_TS" ]
Config2= namedtuple("Config2", Config_fields2)
cfg2= Config2(1 , "GM" , 1 , "Development" , 0 , "3-4.5V circuit chan(0)" , 1 , "BASELINE VERSION" , "2026-4-21_14:20:19" , 25.4 , 4.095 , 32768 , 64 , 1.0e-07 , 99300.0 , 219100.0 , 0.688128140703518 , 0 , "2026-4-21_14:20:19" )
