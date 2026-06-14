Updated on: 06/06/26
LUTS:  added column version so that many versions of LUTS can be stored and retrieved

CREATE TABLE IF NOT EXISTS "LUTS" (ID INTEGER PRIMARY KEY , APP_ID integer, VERSION integer, CHAN integer,  VM real, VIN real );

CONFIG: changed Gain to FSR, added vd_fract, all cols are in caps to match namedtuple

CREATE TABLE IF NOT EXISTS "CONFIG" (ID INTEGER PRIMARY KEY , OWNER varchar,APP_ID integer, APP_DESC varchar, CHAN integer, CHAN_DESC VARCHAR , VERSION     INTEGER NOT NULL, VERSION_DESC VARCHAR,  TIMESTAMP VARCHAR, TEMPC REAL,ADC_FSR real, ADC_STEPS integer, ADC_SAMPLE_RATE INTEGER,  C1 real, R1 REAL, R2 REAL,    VD_FRACT real,  LUT_CALIBRATED integer , LUT_TS VARCHAR );

BMS: added msgid,  version upcased all col names to agree to namedtuple.

CREATE TABLE IF NOT EXISTS "BMS" (ID integer primary key,  MSGID  integer,  VERSION  integer,  TIMESTAMP  varchar,  TYPE  varchar,  CHAN  integer,  A2D_MEAN  real,  VM_MEAN  real,  VM_SD  real,  VB  real,      VIN  real,  ERROR  real,  SAMP_SZ  integer,  DISCARD_SZ  integer,  KEEP_SZ  integer);

A2D: broke out the samples from the BMS table and put them into A2D table synchronizing the bms.id with a2d.bms_id.

CREATE TABLE A2D (ID integer primary key, BMS_ID integer, SAMPLES varchar);

Notes: 
1. In the Config table, there will be 3 records for each app and version : [chan 0, chan 1, chan2]. Each channel will have its own voltage divider resistors, R1,
R2 and therefore its own  VD_FRACT = R2/(R1+R2)
2. The VD_FRACT is used within apps:  
	SqlWorker uses it to populate the LUT Table for each channel. 
    Server computation method uses it to compute vb given vm. vb = vm/vd_fract.  This can also be done and be verified by using the lookuptable. 
3. The A2D samples will not be sent on records of measurements nor calibrations but must be requested when needed using dbi.get_a2d_samples(bms_id).




