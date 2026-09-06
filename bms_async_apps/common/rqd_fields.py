#file: common/rqd_fields.py

'''When msgs are passed through a node, the node classes and methods must provide certain fields so that all rqd fields for the 
   ultimate save to a db_table are populated. The field names will be in all cap chars, some node classes: (adc, svr_task_mgr,svr_dbi, gui) 
   will also be identified. The purpose (or code) will be ~3 digits. Present in this module will be the rqd_fields per class for a table.
   These will be imported as pytest fixtures into unit tests to verify that the module under test is populating its rqd_fields. 
   In setup the unit test will set the value of all fields will be -99 or None. Then the methods under test will populate the fields.
   In the assert phase of the test, fields will be asserted that their value is not -99.
   Since the sqlite app will supply the next ID for every table insertion,"ID" will not be tested. Also VIN will be None unless msg is a calibration.
   VIN for calibrations will have value > 0 . 
'''

#BMS table:
table_fields_bms= { 
"ID" , 
"APP_ID", 
"VERSION" ,
"MSGID", 
"TIMESTAMP", 
"TYPE" , 
"CHAN" ,
"A2D_MEAN", 
"VM_MEAN" , 
"VM_SD" , 
"VB" , 
"VIN", 
"ERROR", 
"SAMP_SZ" , 
"DISCARD_SZ" , 
"KEEP_SZ" , 
"MEAS_ID", 
"REPORTABLE"} 

#bms shared responsibilities:
sql_fields = {"ID"}
svr_task_mgr_fields_bms  ={"A2D_MEAN", "VM_MEAN", "VM_SD", "VB", "ERROR", "DISCARD_SZ", "KEEP_SZ","REPORTABLE"}
adc_fields_bms = {"APP_ID", "VERSION", "MSGID", "TIMESTAMP","TYPE", "CHAN", "VIN", "SAMP_SZ", "MEAS_ID"}
assert sql_fields|svr_task_mgr_fields_bms|adc_fields_bms == table_fields_bms

#AMP_HRS table:
# │ ID │ APP_ID │ VERSION │ MEAS_ID │ TIMESTAMP │ I_MEAN │ ELAPSE_SEC │ AH_USED │ AH_TOTAL │

table_fields_amp_hrs = {
"ID", 
"MEAS_ID", 
"TIMESTAMP", 
"I_MEAN", 
"ELAPSED_SEC", 
"AH_USED", 
"AH_TOTAL"}

#amp_hrs shared responsibilities:
adc_fields_amp_hrs = {"MEAS_ID", "TIMESTAMP", "I_MEAN", "ELAPSED_SEC", "AH_USED"}
svr_task_mgr_fields_amp_hrs= {}
svr_dbi_fields_amp_hrs ={"AH_TOTAL"}
sql_fields_amp_hrs= {"ID"}
assert sql_fields_amp_hrs|adc_fields_amp_hrs|svr_dbi_fields_amp_hrs == table_fields_amp_hrs
