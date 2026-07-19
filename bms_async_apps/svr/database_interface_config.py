# file:database_interface_config.py

from collections import namedtuple

# named tuples... Where they match db table column names they will be upper case.
# APPS: (ID, OWNER,  APP_DESC ,TIMESTAMP  , TEMPC, ADC_FSR, ADC_STEPS, ADC_SAMPLE_RATE, VERSION, VERSION_DESC) 
APP_CONFIG_FIELDS =    ( 'ID', 'OWNER', 'APP_DESC', 'TIMESTAMP',  'TEMPC', 'ADC_FSR', 'ADC_STEPS', 'ADC_SAMPLE_RATE', 'VERSION', 'VERSION_DESC')
                                     
#CHANNELS: ( ID, APP_ID, CHAN,       CHAN_DESC      , VERSION, VERSION_DESC,    TIMESTAMP    ,   C1   ,    R1   ,    R2   ,      SLOPE      , LUT_CALIBRATED,       LUT_TS      , K_FACTOR,     INTERCEPT    )
CHAN_CONFIG_FIELDS = ( 'ID', 'APP_ID', 'CHAN', 'CHAN_DESC', 'VERSION', 'VERSION_DESC',  'TIMESTAMP',  'C1' ,'R1' , 'R2' ,  'SLOPE'  , 'LUT_CALIBRATED',  'LUT_TS'  , 'K_FACTOR' , 'INTERCEPT')
APP_CONFIG = namedtuple( "APP_CONFIG", APP_CONFIG_FIELDS )                                                                        #19 fields
CHAN_CONFIG= namedtuple("CHAN_CONFIG", CHAN_CONFIG_FIELDS)
Abbrev= namedtuple( "Abbrev", ("id", "owner", "app_desc", "version_desc", "channel_id", "channel_desc"))    #6 fields
BMS_FIELDS = ("ID", "MSGID", "VERSION", "TIMESTAMP", "TYPE", "CHAN", "A2D_MEAN", "VM_MEAN", "VM_SD", "VB", "VIN", "ERROR", "SAMP_SZ", "DISCARD_SZ", "KEEP_SZ")

BMS = namedtuple("BMS", BMS_FIELDS )   #16 fields 6/4/2026
# LUTS schema: ID  | app_id | chan |   vm   | vin  | version 
LUT =namedtuple("LUT", ("ID", "APP_ID", "VM", "VIN", "VERSION") )

Lut_Limits = namedtuple( "Lut_Limits", ("circuit_name", "lower_limit", "upper_limit", "length"))



Stats=namedtuple("Stats",("a2d","vm","vm_sd","vb"))


#=== responses ======
#TODO: design handling of the following responses in svr_task_mgr info only
# dict to display the dbi interface codes (cmds) and the arglist for each...

funct_desc = {300: 'save_config(  msg : Config )',       302: 'sync_time()',
                       310: 'get_config( chan : int )',                 320:'save_to_bms( msg :BMS )' ,
                       330: 'list_bms( chan:int, atype:str) ',      340: 'get_bms_a2d_samples( bms_id : int)',
                       350: 'get_lut( chan:int)',                          352: 'get_lut_item(chan:int, vin:float)',
                       360: 'get_lut_timestamp( chan:int )',      370:'update_lut_pair(  _id:int,   vm:float,   vin:float)' ,
                       380: 'update_lut_timestamp( chan:int )', 390: 'get_estimator_parms( )'  }
