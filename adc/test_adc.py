# file: adc/test_adc.py
print("Starting ADC test")

from copy import deepcopy

MEAN_A2D_BY_CHAN = (24558, 19394, 22326)
OFFSETS = (-1, 0, 0, 0)

ADC_TO_SVR_TEMPLATE = { "SENDER":"ADC", "RECEIVER":"SVR", "APP_ID":1, "VERSION":3, "CODE": 101, "MSGID": 123, "MEAS_ID":1, "TYPE":"m", 
    "CHANS":[
    {"CHAN":0, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      
    {"CHAN":1, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      
    {"CHAN":2, "TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "A2D":[24500,24500]},      
    {"CHAN":3, "TIMESTAMP": 178000.0, "I_MEAN":0.550,"PERIOD_SEC":3600, "AH_USED":0.550 } 
    ] 
    }

#The app to be tested...
def adc_fixture():
    """Return the ADC object used by the hardware tests."""
    return adc.ADC(APP_ID, VERSION)

# the fields for which  the adc must provide values
def adc_rqd_fields_fixture():
    """Return a fresh copy of the required ADC fields."""
    adc_fields_bms = {"APP_ID", "VERSION", "MSGID", "TIMESTAMP","TYPE", "CHAN", "VIN", "SAMP_SZ", "MEAS_ID"}
    adc_fields_amp_hrs = {"MEAS_ID", "TIMESTAMP", "I_MEAN", "PERIOD_SEC", "AH_USED"}
    adc_rqd_fields = adc_fields_bms | adc_fields_amp_hrs
    return deepcopy(adc_rqd_fields)

# the report template which the app will populate. It will be tested against expected values.
def report_fixture():
    """Return a fresh report template."""
    return deepcopy(ADC_TO_SVR_TEMPLATE) 

# the expected report filled with expected values. It will be tested against populated report values.
def expected_fixture():
    """Return a fresh report template. It will be modified in the test method with expected values."""
    return deepcopy(ADC_TO_SVR_TEMPLATE)

def vins_fixture():
    """Return the three test input voltages in a list."""
    return [4.0, 8.0, 12.0]

def make_a2d_samples(mean_a2d):
    """Return 64 deterministic samples within one count of the mean."""
    a2d = []
    for index in range(64):
        a2d.append(mean_a2d + OFFSETS[index % len(OFFSETS)])
    return a2d

def a2d_fixture():
    """Return one fresh 64-sample list for each voltage channel."""
    return [
        make_a2d_samples(mean_a2d)
        for mean_a2d in MEAN_A2D_BY_CHAN
]

def amps_chan_fixture():
    """chan 3, I_MEAN, PERIOD_SEC, AH_USED"""
    return [3, 0.87, 3600, 0.87]
####===================tests=======================###
                                                                               
print("test_adc.py is now running on the ESP32")

report = report_fixture()
vins = vins_fixture()

# tests to be run by the runner...
def test_fixtures():
    required_fields = adc_rqd_fields_fixture()
    report = report_fixture()
    vins = vins_fixture()
    a2d = a2d_fixture()
    amps_row = amps_fixture()
    print("a2d:", a2d)
    assert len(vins) == 3, "Expected three VIN values"
    assert len(a2d) == 3, "Expected three A2D channel arrays"
    print("Required fields:", required_fields)
    print("Report template:", report)
    print("VINs:", vins)
    print ("amps_row:", amps_row)

    print("PASS: test_fixtures()")
   
def test_next_meas_id(device):
    '''Does it increment by one?'''
    device.meas_id = 10

    result = device.next_meas_id()

    assert result == 11
    print("PASS: test_next_meas_id()")

def test_measure(device, ch):
    '''Does adc generate a2d array, and ...'''
    print("PASS: test_measure()")

def test_report_channel(n, msg, expected):
    '''Same asserts for chans 0,1,2, but values change per channel. Tests for chan 3 is below... '''
    CHANS = msg["CHANS"]
    chan_n = CHANS[n]
    a2d = chan_n["A2D"] 
    len_a2d = len(a2d) == expected["LEN_A2D"]
    meas_a2d = sum(a2d)/len_a2d
    assert chan_n["CHAN"]==n, f"Each channel tuple must have its chan num {n}"
    assert chan_n["TIMESTAMP"] == expected["TIMESTAMP"], f"Timestamp is wrong, it should be {expected['TIMESTAMP']}"
    assert chan_n["VIN"] == expected["VIN"], f"Vin is wrong, It should be {expected['VIN']}"
    assert chan_n["SAMP_SZ"] == expected["SAMP_SZ"], f"SAMP_SZ is wrong, it should be {expected['SAMP_SZ']}"

    print(f"PASSED  test_channel {n}")

# Decision was made that ADC is synchronous even though it is called from async module: adc_asyncio_client. So no async or await is needed in these tests.
def test_report_amps_chan( msg, expected):
    '''Channel 3 of ADC measures current. This tests if the correct values were put into the report. '''
    chans = report["CHANS"]
    chan3 = chans[3]
    assert chan3["CHAN"]==3
    assert chan3["I_MEAN"]== 0.87 
    assert chan3["PERIOD_SEC"] ==3600
    assert chan3["AH_USED"] == 0.87 
    print("PASSED test_amps_chan()") 

def extract_fields(chans):
    '''Each channel has 5 fields. The first 3 chans are voltage channels. Fourth channel is current (amps) ''' 
    fields = [][]
    for i in range (3):
        chan = chans[i]
        fields[i,0] = chan["CHAN"]
        fields[i][1] = chan["TIMESTAMP"]
        fields[i][2] = chan["VIN"]
        fields[i][3] = chan["SAMP_SZ"]
        fields[i][4] = chan["A2D"]
    chan = chans[3]    #current fields
    fields[3][0] = chan["CHAN"]
    fields[3][1] = chan["TIMESTAMP"]
    fields[3][2] = chan["I_MEAN"]
    fields[3][3] = chan["PERIOD_SEC"]
    fields[3][4] = chan["AH_USED"]

    return  fields


def test_build_report_to_svr(device):
    # set up test ...
    report = report_fixture()
    rqd_fields = adc_rqd_fields_fixture()
    vins = [4.0,8.0,12.0]
    msgid = 1234
    code = 101
    device.a2d =a2d_fixture()
    device.build_report_to_svr(report, msgid, vins, code)

    # see if device (adc) correctly fills out the template copy.
    fields = report.keys()
    assert rqd_fields == fields
    assert report.msgid == msgid
    assert report.code == code
    assert report.a2d == device.a2d
    assert len(report["CHANS"])==4
    chan3 = report["CHANS"][3]
    assert chan3["CHAN"]==3
    assert chan3["I_MEAN"]== 0.87 
    assert chan3["PERIOD_SEC"] ==3600
    assert chan3["AH_USED"] == 0.87 
    print("PASS: test_report_to_svr()")



def run_tests():
    device = adc_fixture()
    test_fixtures()
    test_next_meas_id(device)
    for atype in ['m','c']:
        for ch in range(3):
            await test_measure(device, ch)

    test_build_report_to_svr(device)

    print("PASS: all ADC tests completed")



#=========delete or comment out below this line=======
