#file tests/integration/test_svr_task_manager.py  Handles requests; connects to database_interface to query and update tables.

from svr.svr_task_manager import  SvrTaskManager
from svr.database_interface_config import APP_CONFIG, CHAN_CONFIG, LUT, BMS, BMS_FIELDS, APP_CONFIG_FIELDS, CHAN_CONFIG_FIELDS, AMP_HRS_FIELDS
import json
import pytest
from copy import deepcopy

#TODO 1: Add asserts to tests so that things are tested...
@pytest.fixture
def clean_test_records(stm):
    stm.dbi.delete_test_records()

    try:
        yield
    finally:
        stm.dbi.delete_test_records()

@pytest.fixture
def persisted_reports(stm, measure_report):
    # This assumes measure_report supplies the dictionary
    # shown in your earlier test output.
    measurement = deepcopy(measure_report)
    calibration = deepcopy(calibration_report)

    reports = {"m": measurement, "c": calibration}

    # Setup: remove leftovers from an earlier run.
    stm.dbi.delete_test_records()

    try:
        stm.save_report(measurement)
        stm.save_report(calibration)

        yield reports

    finally:
        # Teardown: also runs when a test assertion fails.
        stm.dbi.delete_test_records()

#to save amp_hrs
@pytest.fixture
def amp_hrs():
    # ID │ APP_ID │ VERSION │ MEAS_ID │TIMESTAMP │ I_MEAN │ PERIOD_SEC │ AH_USED │ AH_TOTAL │
    return  deepcopy({"ID": "NULL", "APP_ID": 1, "VERSION": 3, "CHAN":3, "MEAS_ID": 99999, "TIMESTAMP": 1780000.01, "I_MEAN": 0.550, "PERIOD_SEC": 3600, "AH_USED":0.550} )

@pytest.fixture
def a2d_0():
    return [ 9088, 25199, 25199, 25199, 25199, 25200, 25200, 25198, 25199, 25199, 25199, 25199, 25200, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25200, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25200, 25199, 25199, 25198, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199, 25199] 

@pytest.fixture
def a2d_1():
    return [9088, 20641, 20640, 20641, 20640, 20640, 20641, 20640, 20640, 20640, 20641, 20640, 20640, 20640, 20641, 20640, 20640, 20640, 20641, 20640, 20640, 20640, 20641, 20640, 20640, 20640, 20641, 20640, 20640, 20640, 20641, 20640, 20640, 20640, 20641, 20640, 20640, 20640, 20640, 20641, 20640, 20640, 20640, 20641, 20640, 20640, 20640, 20641, 20640, 20640, 20640, 20641, 20640, 20640, 20640, 20641, 20640, 20640, 20640, 20641, 20640, 20640, 20640, 20641]

@pytest.fixture
def a2d_2():
    return  [2060, 23120, 23120, 23120, 23120, 23120, 23121, 23120, 23120, 23120, 23120, 23121, 23120, 23122, 23120, 23120, 23120, 23121, 23120, 23120, 23120, 23120, 23121, 23120, 23120, 23120, 23120, 23121, 23120, 23120, 23120, 23120, 23121, 23120, 23120, 23120, 23120, 23121, 23120, 23120, 23120, 23121, 23120, 23120, 23120, 23120, 23120, 23121, 23120, 23120, 23120, 23120, 23121, 23120, 23120, 23120, 23120, 23121, 23120, 23120, 23120, 23120, 23121, 23120]

@pytest.fixture
def measure_report(a2d_0, a2d_1, a2d_2):
    return  {'RECEIVER': 'SVR', 'CODE': 31, 'MEAS_ID': 9998, 'VERSION': 3, 'SENDER': 'ADC', 'MSGID': 156, 'TYPE': 'm', 'APP_ID': 1, 'CHANS': [ {'CHAN': 0, 'TIMESTAMP': 844677937, 'VIN': None,'SAMP_SZ': 64, 'A2D':a2d_0} ,{'CHAN': 1, 'TIMESTAMP': 844677938, 'VIN': None,'SAMP_SZ': 64, 'A2D': a2d_1 }, {'CHAN': 2, 'TIMESTAMP': 844677939, 'VIN': None, 'SAMP_SZ': 64, 'A2D':a2d_2 }, {'CHAN': 3, 'TIMESTAMP': 844677939, 'I_MEAN': 0.55, 'PERIOD_SEC': 844677952.0, 'AH_USED': 0.55, }]}

@pytest.fixture
def calibration_report(a2d_0, a2d_1, a2d_2):
    return  {'RECEIVER': 'SVR', 'CODE': 31, 'MEAS_ID': 9999, 'VERSION': 3, 'SENDER': 'ADC', 'MSGID': 156, 'TYPE': 'c', 'APP_ID': 1, 'CHANS': [ {'CHAN': 0, 'TIMESTAMP': 844677937, 'VIN': 4.11,'SAMP_SZ': 64, 'A2D':a2d_0 },{'CHAN': 1, 'TIMESTAMP': 844677938, 'VIN': 8.26,'SAMP_SZ': 64, 'A2D':a2d_1},{'CHAN': 2, 'TIMESTAMP': 844677939, 'VIN': 12.43, 'SAMP_SZ': 64, 'A2D': a2d_2 },  {'CHAN': 3, 'TIMESTAMP': 844677939, 'I_MEAN': 0.55, 'PERIOD_SEC': 844677952.0, 'AH_USED': 0.55, }]}


@pytest.fixture
def rpt():
    return { "SENDER":"ADC", "RECEIVER":"SVR", "APP_ID":1, "VERSION":3, "CODE": 101, "MSGID": 123, "MEAS_ID":1, "TYPE":"m", "CHANS":[ 
           {"CHAN":0, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #A2D will have 64 values.. just dummy here... 
           {"CHAN":1, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #likewise
           {"CHAN":2, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      #likewise
           {"CHAN":3, "TIMESTAMP": 178000.0, "I_MEAN":0.550,"PERIOD_SEC":3600, "AH_USED":0.550 } # values will vary but no arrays...
         ] }


#Computed_BMS_FIELDS: │ A2D_MEAN │ VM_MEAN │  VM_SD  │ VB  │  VIN  │ ERROR │ DISCARD_SZ │ KEEP_SZ 
@pytest.fixture
def computed_bms_fields():
    return [{"A2D_MEAN": 25199.0, "VM_MEAN": 3.1499, "VM_SD": 4.167e-05, "VB": 4.2226, "VIN": 4.11, "ERROR": -0.1126, "DISCARD_SZ": 1, "KEEP_SZ":63},
            {"A2D_MEAN": 20640.3, "VM_MEAN": 2.58,   "VM_SD": 5.561e-05, "VB": 7.7576, "VIN": 8.26, "ERROR": 0.5024,  "DISCARD_SZ": 1, "KEEP_SZ":63},
            {"A2D_MEAN": 23120.2, "VM_MEAN": 2.89,   "VM_SD": 4.939e-05, "VB": 11.604, "VIN": 12.43,"ERROR": 0.8260,  "DISCARD_SZ": 2, "KEEP_SZ":62}
           ] 


@pytest.fixture
def stm():
    return SvrTaskManager(1,3)

@pytest.mark.parametrize(
            "code,arglist",
    [
      pytest.param(4, [], id="4-max-meas-id"),
      pytest.param(10, [], id="10-get_app_config" ),
      pytest.param(20, [0], id="20-get_chan_config" ),
      pytest.param(20, [1], id="20-get_chan_config" ),
      pytest.param(20, [2], id="20-get_chan_config" ),
      pytest.param(31, ["measure_report"], id="31-save_report" ),
      pytest.param(41, ["calibration_report"], id="41-save_report" ),
      #pytest.param(33, ["measure_report"], id="33-save_report" ),
      #pytest.param(43, ["calibration_report"], id="43-save_report" ),
      #pytest.param(50, ["bms_dict"], id="50-save_to_bms"),       #This is deprecated, because save_report does it as part of a transaction, that updates three tables.
      pytest.param(52, [0, "m"], id="30-list-chan0-measure"),
      pytest.param(52, [0, "c"], id="30-list-chan0-calibrate"),
      pytest.param(52, [1, "m"], id="30-list-chan1-measure"),
      pytest.param(52, [1, "c"], id="30-list-chan1-calibrate"),
      pytest.param(52, [2, "m"], id="30-list-chan2-measure"),
      pytest.param(52, [2, "c"], id="30-list-chan2-calibrate"),
      pytest.param(54, [5], id="54-get_bms_a2d_samples"),
      pytest.param(60, [], id="60-get_ah_total"),
      #pytest.param(62, ["amp_hrs"], id="62-save_amp_hrs"),
      #pytest.param(66, [ ], id="66-delete_test_amp_hrs"),
      pytest.param(70, [0], id="70-get_lut"),
      pytest.param(70, [1], id="70-get_lut"),
      pytest.param(70, [2], id="70-get_lut"),
      pytest.param(80, [0], id="80-get_estimator_parms"),
      pytest.param(80, [1], id="80-get_estimator_parms"),
      pytest.param(80, [2], id="80-get_estimator_parms"),
    ],
)

def test_call_function(stm, code, arglist, request, clean_test_records):
    # Replace the fixture name with its returned dictionary.
    if code in (31, 41, 50, 62):
        fixture_name = arglist[0]
        arglist = [request.getfixturevalue(fixture_name)]

    handler = stm.funct_dict[code]

    print(f"Testing code: {code}, function: {handler.__name__}")
    print(f"arglist: {arglist}")

    result = handler(*arglist)
    print(result)

#TODO: Fix the test_persisted_voltages test parameters and method...

@pytest.mark.parametrize(
            "chan,atype,rpt",
    [
     pytest.param(0, 'm',"measure_report", id="0-'m'-measure_report"),
     pytest.param(1, 'm',"measure_report", id="1-'m'-measure_report"),
     pytest.param(2, 'm',"measure_report", id="2-'m'-measure_report"),

     pytest.param(0, 'c',"calibration_report", id="0-'c'-calibration_report"),
     pytest.param(1, 'c',"calibration_report", id="1-'c'-calibration_report"),
     pytest.param(2, 'c',"calibration_report", id="2-'c'-calibration_report"),
    ])

def test_persisted_voltage(chan, atype, rpt, clean_test_records, computed_bms_fields,  stm, request):
    stm.dbi.delete_test_records()
    rpt = request.getfixturevalue(rpt)
    meas_id = rpt["MEAS_ID"]
    try:
        stm.save_report(rpt)

        bms = [[],[],[]]
        a2d = [[],[],[]]
        amp_hrs = stm.dbi.get_amp_hrs_by_meas_id( meas_id)
        assert amp_hrs is not None

        for ch in range(3):
            computed = computed_bms_fields[ch]
            row = stm.dbi.get_measurement_report_for_chan(meas_id, ch)
            assert row is not None
            bms[ch] = BMS(*row)
            print("Returned:", repr(bms[ch]), "Type:", type(bms[ch]))
            assert bms[ch] is not None
            bms_id = bms[ch][0]
            row = stm.dbi.get_bms_a2d_samples(bms_id)
            assert row is not None
            a2d[ch] = json.loads(row[0])

            expected = rpt["CHANS"][ch]
            actual = bms[ch]
            assert actual.MEAS_ID == rpt["MEAS_ID"]
            assert actual.APP_ID == rpt["APP_ID"]
            assert actual.VERSION == rpt["VERSION"]
            assert actual.TYPE == atype
            assert actual.CHAN == ch
            assert int(actual.TIMESTAMP) == expected["TIMESTAMP"]
            assert actual.SAMP_SZ == len(expected["A2D"])

            # Computed BMS Fields:

            assert actual.A2D_MEAN == pytest.approx(computed["A2D_MEAN"], abs=0.1)
            assert actual.VM_MEAN == pytest.approx(computed["VM_MEAN"], abs=0.0001)
            assert actual.VM_SD == pytest.approx(computed["VM_SD"], abs=1e-8)
            assert actual.VB == pytest.approx(computed["VB"], abs=0.0001)

            assert actual.DISCARD_SZ == computed["DISCARD_SZ"]
            assert actual.KEEP_SZ == computed["KEEP_SZ"]

            assert a2d[ch] == expected["A2D"]

            if atype == "m":
                assert actual.VIN is None
                assert actual.ERROR is None
            else:
                assert actual.VIN == pytest.approx(expected["VIN"])
                assert actual.ERROR == pytest.approx(computed["ERROR"], abs=0.0001)

        #print(f"BMS: {bms}")
        #print(f"Returned A2D: {a2d}") 
        #print(f"Returned AMP_HRS: {amp_hrs}")
    finally:
        # Teardown: also runs when a test assertion fails.
        stm.dbi.delete_test_records()

''' =========delete or comment out below this line========
 
'''
