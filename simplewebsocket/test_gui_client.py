# file test_gui_client.py
import json
from collections import namedtuple,OrderedDict
import database_interface_config as dic
from  lut_convert import  LutConvert as LC
import re

cfg_msg = "350 : [Config(id=1, owner='GM', app_id=1, app_desc='Development', chan=0, chan_desc='4.2V CIRCUIT CHANNEL(0)', version=1, version_desc='BASELINE VERSION', creation_time='2025-12-12_22-39-56', mosfet=1, mosfet_type='P-CHANNEL', tempC=25.4, ADC_GAIN=0, ADC_SAMPLE_RATE=3, r1=0.0, r2=1000.0, rp=10000.0, rg=220.0, LUT_CALIBRATED=0, LUT='[[2.0: 2.5], [2.095: 2.6], [2.19: 2.7], [2.285: 2.8], [2.38: 2.9], [2.475: 3.0], [2.57: 3.1], [2.665: 3.2]    , [2.76: 3.3], [2.855: 3.4], [2.95: 3.5], [3.045: 3.6], [3.1399998: 3.7], [3.2350002: 3.8], [3.33: 3.9],       [3.425: 4.0], [3.52: 4.1], [3.615: 4.2], [3.71: 4.3], [3.805: 4.4], [3.9: 4.5] ]', LUT_TS='2026-2-24_17:00'), Config(id=2, owner='GM', app_id=1, app_desc='Development', chan=1, chan_desc='8.4 V CIRCUIT CHANNEL(1)', version=1, version_desc='BASELINE VERSION', creation_time='2025-12-12_22-39-56', mosfet=2, mosfet_type='P-CHANNEL', tempC=25.4, ADC_GAIN=1, ADC_SAMPLE_RATE=3, r1=1000.0, r2=510.0, rp=10000.0, rg=480.0, LUT_CALIBRATED=0, LUT='[[2.0277596: 5.0], [2.0784536: 5.1], [2.1291476: 5.2], [2.1798416: 5.3], [2.2305356: 5.4], [2.2812296: 5.5],                [2.3319236: 5.6], [ 2.3826174: 5.7], [2.4333114: 5.8], [2.4840054: 5.9], [2.5346994: 6.0], [2.31964: 6.108], [2.367615: 6.208], [2.419357: 6.299],               [2.466862: 6.398], [2.514136: 6.5], [2.561819: 6.6], [2.608113: 6.7], [2.655522: 6.8], [2.70166: 6.9], [2.74978: 7.0], [2.79551: 7.1], [2.84887: 7.2],                  [2.898994: 7.3],     [2.953952: 7.4], [3.007714: 7.5], [3.060575: 7.6], [3.113444: 7.7], [3.168053: 7.8], [3.221899: 7.9], [3.275012: 8.0], [3.328626: 8.1],           [3.381747: 8.2], [3.435036: 8.3], [3.488835: 8.4], [3.544073: 8.5], [3.598066: 8.6], [3.651918: 8.7], [3.706656: 8.8], [3.759773: 8.9], [3.808737: 9.0 ] ]', LUT_TS='2026-2-24_17:07'), Config(id=3, owner='GM', app_id=1, app_desc='Development', chan=2, chan_desc='12.6 V CIRCUIT CHANNEL(2)', version=1, version_desc='BASELINE VERSION', creation_time='2025-12-12_22-39-56', mosfet=3, mosfet_type='P-CHANNEL', tempC=25.4, ADC_GAIN=1, ADC_SAMPLE_RATE=3, r1=1000.0, r2=330.0, rp=10000.0, rg=480.0, LUT_CALIBRATED=0, LUT='{2.25: 7.5, 2.266667: 7.6, 2.2833332: 7.7, 2.3000002: 7.8, 2.3166666: 7.9, 2.3333336: 8.0, 2.35: 8.1, 2.3666668: 8.2, 2.3833332: 8.3, 2.4: 8.4, 2.4166668: 8.5, 2.4333334: 8.6, 2.45: 8.7, 2.4666668: 8.8, 2.4833334: 8.9, 2.5: 9.0, 2.516667: 9.1, 2.5333332: 9.2, 2.5500002: 9.3, 2.5666666: 9.4, 2.5833336: 9.5, 2.6: 9.6, 2.6166668: 9.7, 2.6333334: 9.8, 2.65: 9.9, 2.6666664: 10.0, 2.6833334: 10.1, 2.7: 10.2, 2.7166668: 10.3, 2.7333336: 10.4, 2.75: 10.5, 2.7666666: 10.6, 2.7833332: 10.7, 2.8000002: 10.8, 2.8166666: 10.9, 2.8333336: 11.0, 2.85: 11.1, 2.8666668: 11.2, 2.8833334: 11.3, 2.9: 11.4, 2.9166664: 11.5, 2.9333334: 11.6, 2.95: 11.7, 2.9666668: 11.8, 2.9833336: 11.9, 3.0: 12.0, 3.0166666: 12.1, 3.0333336: 12.2, 3.05: 12.3, 3.0666666: 12.4, 3.0833336: 12.5, 3.1000002: 12.6, 3.1166666: 12.7, 3.1333334: 12.8, 3.15: 12.9, 3.1666668: 13.0, 3.1833334: 13.1, 3.2: 13.2, 3.2166668: 13.3, 3.2333334: 13.4, 3.25: 13.5}', LUT_TS='2025-9-29_20-20-36')]"
purpose=cfg_msg[0:3]
cfgs=cfg_msg[4:].split("Config")
cfg0 = cfgs[1].split(",")
cfg1 = cfgs[2].split(",")
cfg2 = cfgs[3].split(",")

# jcfg0 = json.loads(cfg0)
print("Channel 0: 3-4.5V")
for c in cfg0:
    print(c)
print("--------------------------------")

print("Channel 1: 6.0-9.0 V") 
for c in cfg1:
    print(c)
print("--------------------------------")
    
print("Channel 2: 9.0-13.5  V") 
for c in cfg2:
    print(c)
print("--------------------------------")
   
lut0 =  cfg0[19:-1][5:]
lut1= cfg1[19:-1][5:]
lut2 = cfg2[19:-1][5:]

def create_ordered_dict( lut, od):
    # drop 1st and last two elements in the lut to avoid '{'  and ' }'  and timestamp.
    for c in lut[:-2]:
        w=re.sub("\[", "", c).strip()
        z=re.sub("\[", "", w).strip()
        pr=z.split(":")
        x=float(pr[0].strip())
        y=float(pr[1][:-1].strip())
    
        print(f"c: {c}  pr: { x},{y}")
        if len(pr) == 2:
            od[float(x)] = float(y)
    print("orderedDict: ",od)
    return od

self.luts[0]=luts[0]
self.luts[1]=luts[1]
self.luts[2]=luts[2]


luts = [OrderedDict(),OrderedDict(),OrderedDict()]

luts[0]=create_ordered_dict(lut0,luts[0])
luts[1]=create_ordered_dict(lut1,luts[1])
luts[2]=create_ordered_dict(lut2,luts[2])
 
print(f"Lut0 : {luts[0]}")
print(f"Lut1 : {luts[1]}")
print(f"Lut2 : {luts[2]}")

 
 
 
 

