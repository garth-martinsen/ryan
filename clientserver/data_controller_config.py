# file: data_controller_config
from collections import namedtuple

# named tuples
Lut_Limits = namedtuple(
    "Lut_Limits", ("circuit_name", "vm_low", "vb_low", "vm_high", "vb_high", "length")
)


lsb = 4 / pow(2, 15)
circuits = ["C42", "C84", "C126"]  # indexed by [0,1,2]
dbpath = "/Users/garth/DEV/ryan/clientserver/data/rt_db"

MESSAGE_PURPOSES ={0: "HELLO", 1: "WELCOME CLIENT", 10: "rqst_cfg_ids", 11:"cfg_ids",
                   20: "lut0_rqst", 21: "lut0",  30:"lut1_rqst", 31: "Lut1", 40: "lut2_rqst", 41: "lut2",
                   50: "READY", 51: "READY_OK",  60: "config_rqst", 61: "configs", 100: "rqst_measure_chan",
                   101: "chan_measure",  150: "rqst_schedule_measure", 175: "get_meas_records",
                   176: "measurement_records",  200: "rqst_calib_chan_vin",   201: "calib_chan_vin",
                   250: "rqst_step_calib",  275: "get_calib_records", 276: "calib_records",
                   300: "get_lut_chan",  400: " get_last_keep"}
