All Schemas in rt_db: as of 6/29/26
 CREATE TABLE "CONFIG" (ID INTEGER PRIMARY KEY , OWNER varchar,APP_ID integer, APP_DESC varchar, CHAN integer, CHAN_DESC VARCHAR , version     INTEGER NOT NULL, VERSION_DESC VARCHAR,  TIMESTAMP VARCHAR, TEMPC REAL,ADC_FSR real, ADC_STEPS integer, ADC_SAMPLE_RATE INTEGER,  C1 real, R1 REAL, R2 REAL,    VD_FRACT real,  LUT_CALIBRATED integer , LUT_TS VARCHAR , K_FACTOR) 


 CREATE TABLE "BMS" (ID integer primary key,  MSGID  integer,  VERSION  integer,  TIMESTAMP  varchar,  TYPE  varchar,  CHAN  integer,  A2D_MEAN  real,  VM_MEAN  real,  VM_SD  real,  VB  real,      VIN  real,  ERROR  real,  SAMP_SZ  integer,  DISCARD_SZ  integer,  KEEP_SZ  integer)                                                                                          

Notes: 
1. In the Config table, there will be 3 records for each app and version : [chan 0, chan 1, chan2]. Each channel will have its own voltage divider resistors, R1,
R2 and therefore its own  VD_FRACT = R2/(R1+R2)
2. The VD_FRACT is used within apps:  
	SqlWorker uses it to populate the LUT Table for each channel. 
    Server computation method uses it to compute vb given vm. vb = vm/vd_fract.  This can also be done and be verified by using the lookuptable. 
3. The A2D samples will not be sent on records of measurements nor calibrations but must be requested when needed using dbi.get_a2d_samples(bms_id).
4. The MSGID table will furnish the next_msgid when requested. It will increment by 1 each new row in the table. See code in svr_task_mgr.py to see example.
