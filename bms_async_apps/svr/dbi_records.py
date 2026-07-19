# file: dbi_records.py   used to past records used in development so they can be loaded into rt_db

from  .database_interface_config import APP_CONFIG, CHAN_CONFIG, BMS, Stats
#config records

chan_configs=[[],[],[]]
# APP_CONFIG_FIELDS( 'ID', 'OWNER', 'APP_DESC', 'TIMESTAMP',  'TEMPC', 'ADC_FSR', 'ADC_STEPS', 'ADC_SAMPLE_RATE', 'VERSION', 'VERSION_DESC')
app_config = APP_CONFIG(1, 'GM', 'Development', 1784096813.4462662, 25.4, 4.096, 32768, 64, 3, 'PCB2')
# CHAN_CONFIG_FIELDS = ( 'ID', 'APP_ID', 'CHAN', 'CHAN_DESC', 'VERSION', 'VERSION_DESC',  'TIMESTAMP',  'C1' ,'R1' , 'R2' ,  'SLOPE'  , 'LUT_CALIBRATED',  'LUT_TS'  , 'K_FACTOR' ,'INTERCEPT')
chan_configs[0] = CHAN_CONFIG(1,  1, 0,  'One Cell 3.0-4.5V',      3, 'PCB2',   1784096813.44626, 1e-07, 101100,  303700, 1.3328943035890672, 0, 1782687301.5675 ,3.0,  0.02233 )
chan_configs[1] = CHAN_CONFIG(2, 1 , 1, 'Two Cells 6.0-9.0V',     3 , 'PCB2' , 1782687301.57536, 1e-07,  222200, 111800, 2.9874776386404265, 0, 1782687301.5753, 3.0,  0.04379 )
chan_configs[2] = CHAN_CONFIG(3, 1, 2,  'Three Cells 9.0-13.5V', 3, 'PCB2',  1782687301.57536, 1e-07,  301100, 99400,    4.029175050301816, 0, 1782687301.5753, 3.0,   0.06689 )

# bms records
# 6/2/26 CREATE TABLE IF NOT EXISTS "BMS" ( id integer primary key, timestamp varchar, type varchar,chan integer,vin real, error real, a2d_mean integer, vm_mean real, vm_sd real, vb real, samples varchar, discard_sz, keep_sz, samp_sz);
#3/14/26 21:37: CREATE TABLE BMS ( id integer primary key, timestamp varchar, type varchar,chan integer,sample_period real, store_time real, gate_time real,  vin real, error real, a2d integer, vm real, vm_sd real, vb real, samples varchar);
# foney data:
samples=[[],[],[]]
samples[0]='[22657, 22654, 22651, 22653, 22655, 22657, 22651, 22657, 22651, 22655, 22657, 22653, 22656, 22658, 22656, 22658, 22657, 22655, 22653, 22655, 22655, 22655, 22655, 22656, 22651, 22658, 22656, 22658, 22658, 22653, 22652, 22658, 22658, 22653, 22655, 22657, 22654, 22651, 22653, 22655, 22657, 22651, 22657, 22651, 22655, 22657, 22653, 22656, 22658, 22656, 22658, 22657, 22657, 22654, 22651, 22653, 22655, 22657, 22651, 22657, 22651, 22655, 22657, 22653]'
samples[1]='[21657, 21654, 21651,21653, 21655, 21657, 21651, 21657, 21651, 21655, 21657, 21653, 21656, 21658, 21656, 21658, 21657, 21655, 21653, 21655, 21655, 21655, 21655, 21656,21651, 21658, 21656, 21658, 21658, 21653, 21652, 21658, 21658, 21653,  21655,21657, 21656,  21653, 21654, 21656, 21658, 21656, 21655, 21658, 21651, 21651,21654, 21656, 21651, 21652, 21654,21655, 21655, 21652, 21654, 21658, 21655,21656, 21658, 21657, 21656, 21657, 21652, 21653]'
samples[2]= '[21033, 21038, 21038, 21037, 21035, 21038, 21036, 21039, 21035, 21036, 21038, 21036, 21035, 21034, 21034, 21036, 21034, 21035, 21034, 21039, 21037, 21039, 21033, 21039, 21038, 21038, 21033, 21036, 21039, 21036, 21039, 21038, 21035, 21035, 21033, 21035, 21035, 21036, 21034, 21037, 21035, 21033, 21033, 21038, 21034, 21036, 21036, 21038, 21034, 21039, 21036, 21036, 21035, 21038, 21033, 21037, 21033, 21036, 21037, 21033, 21037, 21038, 21034, 21035, 21037]'
answers = [[],[],[]]
answers[0]= Stats(22654 ,2.8311, 0.000316, 3.7736)
answers[1]= Stats( 21655, 2.7062, 0.00028, 8.0848)
answers[2]= Stats( 21035, 2.6287, 0.000266,10.4964)

lut_answers0=(3.0, 4.5)
lut_answers1=(6.0, 9.0)
lut_answers2=(9.0, 13.5)
lut_answers = [lut_answers0, lut_answers1, lut_answers2]

#6/6/26: BMS_FIELDS = ("ID", "MSGID", "VERSION", "TIMESTAMP", "TYPE", "CHAN",  "VIN",  "SAMP_SZ", "DISCARD_SZ", "KEEP_SZ", "SAMPLES")
# Fiends missing until computed: "A2D_MEAN", "VM_MEAN", "VM_SD", "VB", "ERROR"
bms=[[],[],[],[],[],[]]
bms[0] = BMS(1, 5010, 3, '2026-3-21 20:34:25', 'c', 0,  22654, 2.83175, 0.000316, 4.113, 4.114, -0.001, 64, 2, 62 )
bms[1] = BMS(2, 5010, 3, '2026-3-14 19:43:55', 'c', 1,  21036 , 2.629, 0.000239, 7.856, 7.9,  0.0444505, 64,2,62 )
bms[2] = BMS(3, 5010, 3, '2026-3-14 19:43:55', 'c', 2,  21036, 2.629, 0.000239, 10.498, 10.5,  -0.002,     64, 2, 62)
