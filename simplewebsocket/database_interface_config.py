# file:database_interface_config.py

from collections import namedtuple

# named tuples... Where they match db table column names they will be upper case.

CONFIG_FIELDS =    ( 'ID', 'OWNER', 'APP_ID', 'APP_DESC', 'CHAN', 'CHAN_DESC', 'VERSION', 'VERSION_DESC', 'CREATION_TIME', 'TEMPC', 'ADC_FSR', 'ADC_STEPS', 'ADC_SAMPLE_RATE', 'C1', 'R1', 'R2', 'VD_FRACT', 'LUT_CALIBRATED', 'LUT_TS')

Config = namedtuple( "Config", CONFIG_FIELDS)                                                                         #19 fields

Abbrev= namedtuple( "Abbrev", ("id", "owner", "app_desc", "version_desc", "channel_id", "channel_desc"))    #6 fields
BMS_FIELDS = ("ID", "MSGID", "VERSION", "TIMESTAMP", "TYPE", "CHAN", "A2D_MEAN", "VM_MEAN", "VM_SD", "VB", "VIN", "ERROR", "SAMP_SZ", "DISCARD_SZ", "KEEP_SZ", "SAMPLES")

BMS = namedtuple("BMS", BMS_FIELDS )   #16 fields 6/4/2026
# LUTS schema: ID  | app_id | chan |   vm   | vin  | version 
LUT =namedtuple("LUT", ("ID", "APP_ID", "VM", "VIN", "VERSION") )

Lut_Limits = namedtuple( "Lut_Limits", ("circuit_name", "lower_limit", "upper_limit", "length"))



Stats=namedtuple("Stats",("a2d","vm","vm_sd","vb"))

#db_path = '/Users/garth/DEV/ryan/clientserver/data/rt_db'
#db_path = '/Users/garth/DEV/ryan/simplewebsocket/data/rt_db'
#db_path =   '/Users/garth/MERGE/ryan/sqliteDB/rt_db'
db_path =   '/Users/garth/DEV/ryan/sqliteDB/rt_db'

#message purposes: note that responses from the db or adc will have 1 added to rqst code, eg : 100 -> 101 etc.
purposes = dict()
purposes[100]='request_measure'                      #all chans 
purposes[101]='response_measurement'
purposes[150]= 'past_measurements_0'            #chan 0
purposes[152]= 'past_measurements_1'           #chan 1
purposes[154]= 'past_measurements_2'           #chan 2
purposes[175]='set_up_periodic_measurements'
purposes[200]='request_calibrate_0'
purposes[201]='response_calibration'
purposes[202]='request_calibrate_1'
purposes[203]='response_calibration_1'
purposes[204]='request_calibrate_1'
purposes[205]='response_calibration_2'
purposes[250]='request_past_calibrations_0'
purposes[252]='request_past_calibrations_1'
purposes[254]='request_past_calibrations_2'
purposes[300]= 'save_config'
purposes[310]= 'request_config'
purposes[311]= 'response_config'
purposes[350]= 'save_lut'
purposes[360]= 'request_lut_0'
purposes[361]= 'responselut_0'
purposes[362]= 'request_lut_1'
purposes[363]= 'response_lut_1'
purposes[364]= 'request_lut_2'
purposes[365]= 'response_lut_2'
purposes[370]= 'request_lut0_timestamp'
purposes[371]= 'response_lut0_timestamp'
purposes[372]= 'request_lut1_timestamp'
purposes[373]= 'response_lut1_timestamp'
purposes[374]= 'request_lut2_timestamp'
purposes[375]= 'response_lut2_timestamp'


# join example: select cfg.id, cfg.owner, cfg.app_desc, cfg.channel_desc, cfg.version_desc, bms.timestamp, bms.a2d, bms.a2d_sd, bms.vm, bms.vb, bms.keep, bms.sample_period, bms.store_time, bms.gate_time  from CONFIG as cfg INNER JOIN  BMS as bms on cfg.id=bms.id;
# BMS join A2D example: select * from BMS bms join A2D a2d on bms.id= a2d.bms_id;   note: first two fields of A2D should be ignored: (id and bms_id)