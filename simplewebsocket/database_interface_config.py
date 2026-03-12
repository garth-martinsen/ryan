# file:database_interface_config.py

from collections import namedtuple

# named tuples
Lut_Limits = namedtuple( "Lut_Limits", ("circuit_name", "lower_limit", "upper_limit", "length"))

CONFIG_FIELDS =    (
        "id",
        "owner",
        "app_id",
        "app_desc",
        "chan",
        "chan_desc",
        "version",
        "version_desc",
        "creation_time",
        "tempC",
        "ADC_GAIN",
        "ADC_SAMPLE_RATE",
        "C1",
        "r1",
        "r2",
        "LUT_CALIBRATED",
        "LUT_TS"
    )

Config = namedtuple( "Config", CONFIG_FIELDS)                                                                         #17 fields

Abbrev= namedtuple( "Abbrev", ("id", "owner", "app_desc", "version_desc", "channel_id", "channel_desc"))    #6 fields

# fields 0 -6 populated by ADC ,  fields 7-11 populated by calculations by (gui_client or databaseInterface)
BMS_FIELDS = (
    'id',
    'timestamp',
    'type',
    'chan',
    'vin',
    'store_time',
    'sample_period',
    'a2d_mean',
    'a2d_sd',
    'vm',
    'vb',
    'error',
)

BMS = namedtuple("BMS", BMS_FIELDS )   #12 fields

LUT =namedtuple("LUT", ("vm", "vin") )
               
#db_path = '/Users/garth/DEV/ryan/clientserver/data/rt_db'
db_path = '/Users/garth/DEV/ryan/simplewebsocket/data/rt_db'

#message purposes: note that responses from the db or adc will have 1 added eg : 100 -> 101 etc.
purposes = dict()
purposes[100]='request_measure'
purposes[101]='response_measurement'
purposes[150]= 'past_measurements_0'
purposes[152]= 'past_measurements_1'
purposes[154]= 'past_measurements_2'
purposes[200]='request_calibrate'
purposes[201]='response_calibration'
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
