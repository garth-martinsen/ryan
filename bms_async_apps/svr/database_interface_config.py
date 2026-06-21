# file:database_interface_config.py

from collections import namedtuple

# named tuples... Where they match db table column names they will be upper case.

CONFIG_FIELDS =    ( 'ID', 'OWNER', 'APP_ID', 'APP_DESC', 'CHAN', 'CHAN_DESC', 'VERSION', 'VERSION_DESC', 'CREATION_TIME', 'TEMPC', 'ADC_FSR', 'ADC_STEPS', 'ADC_SAMPLE_RATE', 'C1', 'R1', 'R2', 'VD_FRACT', 'LUT_CALIBRATED', 'LUT_TS')

Config = namedtuple( "Config", CONFIG_FIELDS)                                                                         #19 fields

Abbrev= namedtuple( "Abbrev", ("id", "owner", "app_desc", "version_desc", "channel_id", "channel_desc"))    #6 fields
BMS_FIELDS = ("ID", "MSGID", "VERSION", "TIMESTAMP", "TYPE", "CHAN", "A2D_MEAN", "VM_MEAN", "VM_SD", "VB", "VIN", "ERROR", "SAMP_SZ", "DISCARD_SZ", "KEEP_SZ")

BMS = namedtuple("BMS", BMS_FIELDS )   #16 fields 6/4/2026
# LUTS schema: ID  | app_id | chan |   vm   | vin  | version 
LUT =namedtuple("LUT", ("ID", "APP_ID", "VM", "VIN", "VERSION") )

Lut_Limits = namedtuple( "Lut_Limits", ("circuit_name", "lower_limit", "upper_limit", "length"))



Stats=namedtuple("Stats",("a2d","vm","vm_sd","vb"))

#db_path = '/Users/garth/DEV/ryan/clientserver/data/rt_db'
#db_path = '/Users/garth/DEV/ryan/simplewebsocket/data/rt_db'
#db_path =   '/Users/garth/MERGE/ryan/sqliteDB/rt_db'
db_path =   '/Users/garth/DEV/ryan/sqliteDB/rt_db'

#=== responses ======
#TODO: design handling of the following responses in svr_task_mgr info only
'''
functions_dict[100]= self.measure                                                   # []                                   forward to ADC_clien; will result in (3) 101s
functions_dict[150]= self.dbi.list_records                                       # [ chan, atype ]     
functions_dict[175]= self.set_up_periodic                                      # [period, reps]               forward to ADC_client
functions_dict[200]= self.calibrate                                                   # [chan, type, vin]
functions_dict[101]='report_measurement'                                                                          # three responses per 100 request
functions_dict[201]='response_calibration '                                                                         # one response per 200 request
functions_dict[311]= 'response_config embedded: [chan, config field values]'
functions_dict[361]= 'response_lut     embedded: [lut, chan, ...]'
functions_dict[371]= 'response_lut_timestamp  embedded: timestamp'
'''
std_msg = {"sender"}

# join example: select cfg.id, cfg.owner, cfg.app_desc, cfg.channel_desc, cfg.version_desc, bms.timestamp, bms.a2d, bms.a2d_sd, bms.vm, bms.vb, bms.keep, bms.sample_period, bms.store_time, bms.gate_time  from CONFIG as cfg INNER JOIN  BMS as bms on cfg.id=bms.id;
# BMS join A2D example: select * from BMS bms join A2D a2d on bms.id= a2d.bms_id;   note: first two fields of A2D should be ignored: (id and bms_id)