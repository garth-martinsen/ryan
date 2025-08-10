# file:database_interface_config.py

from collections import namedtuple

#named tuples
Lut_Limits = namedtuple("Lut_Limits", ("circuit_name", "lower_limit",
                                               "upper_limit", "length"))
Config = namedtuple("Config", ("id", "owner", "app_id", "app_desc", "channel_id", "channel_description", "version_id","version_description",
                                "creation_time","mosfet","mosfet_type" ,"tempC", "r1","r2","rp","rg","LUT_CALIBRATED", "LUT") )
Short_Record = namedtuple("Short_Record",("id", "owner", "app_desc", "version_desc", "channel_id", "channel_desc"))

BMS = namedtuple("BMS",("cfg_id", "meas_type", "timestamp", "a2d_mean","a2d_sd","vm","vb","vin", "error", "keep", "sample_period","store_time", "gate_time"))

CFG_Columns= ["id","OWNER", "APP_ID", "APP_DESC", "CHANNEL_ID","CHANNEL_DESC","VERSION_ID","VERSION_DESC","TIMESTAMP","MOSFET_ID","MOSFET_TYPE","TEMPC","R1","R2","RP","RG","LUT_CALIBRATED","LUT"]
CFG_values=["id","owner", "app_id", "app_desc",  "channel_id", "channel_description", "version_id", "version_description", "creation_time", "mosfet_id", "mosfet_type", "tempC", "r1","r2","rp","rg", "calibrated", "LUT"]

CALIBRATE = namedtuple("CALIBRATE", ("bms_id","vin","error"))
BMS_Columns= ["id", "cfg_id","meas_type", "timestamp", "a2d_mean", "a2d_sd", "vm", "vb", "sample_period", "store_time", "gate_time"]

db_path ='/Users/garth/Programming/MicroPython/usb/ryan/voltage_divider/data/rt_db'
table = 'CONFIG'
#Schema: CREATE TABLE CONFIG (ID INTEGER PRIMARY KEY , channel_id integer,CHANNEL_DESC VARCHAR  VERSION_ID INTEGER NOT NULL, VERSION_DESC VARCHAR,  TIMESTAMP INTEGER,  MOSFET_ID INTEGER, MOSFET_TYPE VARCHAR, TEMPC REAL, R1 REAL, R2 REAL, RP REAL, RG REAL, LUT_CALIBRATED INTEGER, LUT VARCHAR);
#Schema BMS: CREATE TABLE BMS ( id integer primary key, cfg_id integer, timestamp integer,  a2d real, a2d_sd real, vm real, vb real, keep varchar, sample_period real, store_time real, gate_time real );
# example BMS: 1,1,1750436348, 20005.34, 2.123, 2.111, 3.465,[20045,20046,20047],0.00156,0.000444,1.003
#join example: select cfg.id, cfg.owner, cfg.app_desc, cfg.channel_desc, cfg.version_desc, bms.timestamp, bms.a2d, bms.a2d_sd, bms.vm, bms.vb, bms.keep, bms.sample_period, bms.store_time, bms.gate_time  from CONFIG as cfg INNER JOIN  BMS as bms on cfg.id=bms.id;