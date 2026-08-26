# USAGE: in using module: from common.templates.adc_templates import ADC_TO_SVR_TEMPLATE
ADC_TO_SVR_TEMPLATE = {
    "SENDER":"ADC",
    "RECEIVER":"SVR",
    "APP_ID":1,
    "VERSION":3,
    "CODE": 101,
    "MSGID": 123,
    "MEAS_ID":1,
    "TYPE":"m",
    "CHANS":[ 
               {"CHAN":0, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #A2D will have 64 values.. just dummy here... 
               {"CHAN":1, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #likewise
               {"CHAN":2, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #likewise
               {"CHAN":3, "TIMESTAMP": 178000.0, "I_MEAN":0.550,"PERIOD_SEC":3600, "AH_USED":0.550 } # values will vary but no arrays...
            ]
}

