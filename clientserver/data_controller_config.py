# file: data_controller_config
from collections import namedtuple

# named tuples
Lut_Limits = namedtuple(
    "Lut_Limits", ("circuit_name", "vm_low", "vb_low", "vm_high", "vb_high", "length")
)



circuits = ["C42", "C84", "C126"]  # indexed by [0,1,2]
dbpath = "/Users/garth/DEV/ryan/clientserver/data/rt_db"

MESSAGE_PURPOSES ={0: "HELLO", 1: "WELCOME CLIENT", 10: "rqst_cfg0", 11:"cfg0",
                   12: "rqst_cfg1", 13: "cfg1",  14:"rqst_cfg2", 15: "cfg2",
                   50: "READY", 51: "READY_OK",  100: "rqst_measure_chan",
                   101: "measure_chan",  150: "rqst_schedule_measure", 175: "get_meas_records",
                   176: "measurement_records",  200: "rqst_calib_chan_vin",   201: "calib_chan_vin",
                   250: "rqst_step_calib",  275: "get_calib_records", 276: "calib_records"}
# Note:
# 1. purpose 150 results in many 101 responses and purpose 250 results in many 201 responses
# 2. purpose 175 results in a list<BMS records> and purpose 275 results in a list<BMS records>

C42_steps = [x/10 for x in range(30,46)]
C84_steps = [x/10 for x in range(60, 91)]
C126_steps= [x/10 for x in range(90,136)]