
#USAGE:  in module add:  from common.templates.svr_templates import VOLTAGE_REPORT_TEMPLATE

VOLTAGE_REPORT_TEMPLATE = { "SENDER": "SVR", "RECEIVER": "GUI", "CODE": 101,"MEAS_ID": 1, "ROWS": [ 
    { "ID_": 1, "TIMESTAMP": 1783109112.0, "TYPE": "c", "CHAN": 0, "VCELL": 4.0323, "VTAP": 4.0323 }, 
    { "ID_": 2, "TIMESTAMP": 1783105513.0, "TYPE": "c", "CHAN": 1, "VCELL": 3.976, "VTAP": 7.999 } , 
    { "ID_": 3, "TIMESTAMP": 1783105513.0, "TYPE": "c", "CHAN": 2, "VCELL": 3.976, "VTAP": 11.999 } ,
    { "ID_": 4, "TIMESTAMP": 1783105513.0, "I_MEAN":0.22 , "PERIOD_SEC": 3600, "AH_USED": 0.22 } ] 
}

