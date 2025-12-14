# file:database_interface_config.py

from collections import namedtuple

# named tuples
Lut_Limits = namedtuple( "Lut_Limits", ("circuit_name", "lower_limit", "upper_limit", "length"))

CONFIG_FIELDS =    (
        "id",
        "owner",
        "app_id",
        "app_desc",
        "chan_id",
        "chan_desc",
        "version_id",
        "version_desc",
        "creation_time",
        "mosfet",
        "mosfet_type",
        "tempC",
        "ADC_GAIN",
        "ADC_SAMPLE_RATE",
        "r1",
        "r2",
        "rp",
        "rg",
        "LUT_CALIBRATED",
        "LUT",
        "LUT_TS"
    )

Config = namedtuple( "Config", CONFIG_FIELDS)                                                                         #21 fields

Abbrev= namedtuple( "Abbrev", ("id", "owner", "app_desc", "version_desc", "channel_id", "channel_desc"))    #6 fields

BMS = namedtuple("BMS", ('id', 'timestamp', 'type', 'chan',  'cfg_id', 'a2d',  'a2d_sd', 'sample_sz',  'vin','vm', 'vb',  'error', 'store_time', 'gate_time', 'sample_period',  'keep') )   #16 fields

db_path = '/Users/garth/DEV/ryan/clientserver/data/rt_db'

# join example: select cfg.id, cfg.owner, cfg.app_desc, cfg.channel_desc, cfg.version_desc, bms.timestamp, bms.a2d, bms.a2d_sd, bms.vm, bms.vb, bms.keep, bms.sample_period, bms.store_time, bms.gate_time  from CONFIG as cfg INNER JOIN  BMS as bms on cfg.id=bms.id;
