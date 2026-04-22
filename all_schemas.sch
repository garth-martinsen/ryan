Updated on: 4/21/26
LUTS:

CREATE TABLE LUTS (ID INTEGER PRIMARY KEY , app_id, chan integer,  vm real, vin real);

CONFIG:

CREATE TABLE IF NOT EXISTS "CONFIG" (ID INTEGER PRIMARY KEY , OWNER varchar,APP_ID integer, APP_DESC varchar, CHAN integer, CHANNEL_DESC VARCHAR , VERSION_ID     INTEGER NOT NULL, VERSION_DESC VARCHAR,  TIMESTAMP VARCHAR, TEMPC REAL,ADC_FSR real, ADC_STEPS integer, ADC_SAMPLE_RATE INTEGER, C1 real, R1 REAL,       R2 REAL,VD_FRACT real, LUT_CALIBRATED integer, LUT_TS VARCHAR );


BMS:

CREATE TABLE IF NOT EXISTS "BMS" ( id integer primary key, timestamp varchar, type varchar,chan integer,vin real, error real, a2d_mean integer, vm_mean real, vm_sd real, vb real, samples varchar);

Notes: 
1. In the Config table, there will be 3 records for each app: [chan 0, chan 1, chan2]. Each channel will have its own voltage divider resistors, R1,
R2 and therefore its own  VD_FRACT = R2/(R1+R2)
2. The VD_FRACT is used within the apps:  
	SqlWorker uses it to populate the LUT Table for each channel. 
    The stats method uses it to pad the first and last values in the LUT. If vm is less than 1/2 a vm step, it's vb will be the same 
    as if vm were exactly equal to the vm step. The same holds true for vm less than 1/2 vm step above the last value in the LUT.
