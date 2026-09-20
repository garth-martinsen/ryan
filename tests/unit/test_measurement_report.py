from common.templates.svr_templates import VOLTAGE_REPORT_TEMPLATE
from common.templates.adc_templates import ADC_TO_SVR_TEMPLATE
from svr.measurement_report  import MeasurementReport, msg_to_gui
import pytest
from copy import deepcopy

adc_msg = deepcopy(ADC_TO_SVR_TEMPLATE)
# test inputs, Note: all are stringified dicts.
#fake_msgs=[]
#fake_msgs.append( '{"SENDER":"SVR","RECEIVER":"GUI","CODE":101,"ID_": 239,"MEAS_ID":123,"TIMESTAMP":1785041720.0,"CHAN": 0, "TYPE":"m", "VTAP":4.0437 }' )
#fake_msgs.append( '{"SENDER":"SVR","RECEIVER":"GUI","CODE":101,"ID_": 240,"MEAS_ID":123,"TIMESTAMP":1785041721.0,"CHAN": 1, "TYPE":"m", "VTAP":7.885 }'  )
#fake_msgs.append( '{"SENDER":"SVR","RECEIVER":"GUI","CODE":101,"ID_": 241,"MEAS_ID":123,"TIMESTAMP":1785041722.0,"CHAN": 2, "TYPE":"m", "VTAP":11.9399 }')
#fake_msgs.append( '{"SENDER":"SVR","RECEIVER":"GUI","CODE":101,"ID_": 242,"MEAS_ID":123,"TIMESTAMP":1785286839.0,"CHAN": 3, "TYPE":"a" ,\
#		"LAST_TIMESTAMP":1785283239.0,  "I_MEAN":0.550, "PERIOD_SEC": 3600, "AH_USED":33.0 }')

#@pytest.fixture      # This does not seem to work... the fixture does not seem to be able to add_chan(...)
#def measurement():
# creates a fresh instance of measurement before each function
#	return MeasurementReport( 0.5, adc_msg)

@pytest.fixture      # This does not seem to work... the fixture does not seem to be able to add_chan(...)
def adc_msg():
    return adc_msg

def test_measurement():
     measurement = MeasurementReport( 0.5, adc_msg)
     print(f" measurement: {measurement}")
     assert measurement != None
     assert measurement.meas_id ==123, f"The Measurement obj should have a meas_id equal to {123}"

def test_measurement_has_empty_chan_dict():
     measurement = MeasurementReport( 0.5,adc_msg)
     assert measurement.chans != None
     assert len(measurement.chans) == 0, f"No chan measurements are loaded yet so len should equal {0}"

def test_add_chan_0():
     measurement = MeasurementReport( 0.5,adc_msg)
#     measurement.add_chan(fake_msgs[0])
     assert len(measurement.chans) != 0, f"The chans should now have some chan measurement msg in it."
     assert measurement.chans[0]["CHAN"] == 0, f"The meas_chan stored in chans[0] should have the correct channel: {0}"

def test_add_chan_1():
     measurement = MeasurementReport(0.5), adc_msg
#     measurement.add_chan(fake_msgs[1])
     assert len(measurement.chans) != 0, f"The chans should now have some chan measurement msg in it."
     assert measurement.chans[1]["CHAN"] == 1, f"The meas_chan stored in chans[1] should have the correct channel: {1}"

def test_add_chan_2():
     measurement = MeasurementReport( 0.5,adc_msg)
#     measurement.add_chan(fake_msgs[2])
     assert len(measurement.chans) != 0, f"The chans should now have some chan measurement msg in it."
     assert measurement.chans[2]["CHAN"] == 2, f"The meas_chan stored in chans[2] should have the correct channel: {2}"

def test_add_chan_3():
     measurement = MeasurementReport(0.5,adc_msg)
#     measurement.add_chan(fake_msgs[3])
     assert measurement.chans[3]["CHAN"] == 3, f"The meas_chan stored in chans[2] should have the correct channel: {2}"
     assert measurement.chans[3]["AH_USED"] == 33, f"The AH_USED  stored in chans[3] should be: {33}"
     assert measurement.chans[3]["I_MEAN"] == 0.550 , f"The I_MEAN  stored in chans[3] should be: {0.550}"
     assert measurement.chans[3]["PERIOD_SEC"] == 3600 , f"The PERIOD_SEC  stored in chans[3] should be: {3600}"

def test_validate():
     measurement = MeasurementReport(0.5,adc_msg)
#     measurement.add_chan(fake_msgs[0])
#     measurement.add_chan(fake_msgs[1])
#     measurement.add_chan(fake_msgs[2])
#     measurement.add_chan(fake_msgs[3])
     score = measurement.validate()    
     assert score == True, f"The three voltage channels should all be valid: {True}"
  
def test_format_and_return_report():
     svr_to_gui_msg = deepcopy(VOLTAGE_REPORT_TEMPLATE)
     measurement = MeasurementReport(0.5,adc_msg)
#     measurement.add_chan(fake_msgs[0])
#     measurement.add_chan(fake_msgs[1])
#     measurement.add_chan(fake_msgs[2])
#     measurement.add_chan(fake_msgs[3])
     report = measurement.format_and_return_report(svr_to_gui_msg)     
     rows = report["ROWS"]
     assert len(rows)== 4, f"There should be 3 voltage rows and 1 current row: {4} "
     assert rows[0]["VCELL"] == 4.0437, f"The voltage accross the first cell should be: {4.0437}"
     assert round(rows[1]["VCELL"],4) == 3.8413, f"The voltage accross the 2nd cell should be: {3.8413}" 

# utility for next 4 tests
def prep_report():
     svr_to_gui_msg = deepcopy(VOLTAGE_REPORT_TEMPLATE)
     measurement = MeasurementReport(0.5,adc_msg)
#     measurement.add_chan(fake_msgs[0])
#     measurement.add_chan(fake_msgs[1])
#     measurement.add_chan(fake_msgs[2])
#     measurement.add_chan(fake_msgs[3])
     report = measurement.format_and_return_report(svr_to_gui_msg)
     return report
 
 
def test_voltage_report_for_VTAPS():
    answers= [4.0437, 7.885, 11.9399 ]
    report = prep_report()
    epsilon = .0001
    rows = report["ROWS"]
    for i in range(3):
       assert (rows[i]["VTAP"] -  answers[i]) < epsilon, f" Tap voltage not close enough, {answers[i]} vs {rows[i]["VTAP"]}" 
    
def test_voltage_report_for_VCELLS():
    answers= [4.0437, 3.8413, 4.0549 ]
    report = prep_report()
    epsilon = .0001
    rows = report["ROWS"]
    for i in range(3):
        assert rows[i]["VCELL"] -answers[i] < epsilon, f"VCELL value is not close enough, {answers[i]} vs {rows[i]["VCELL"] }" 

def test_voltage_report_for_current_status():
    answers= [0.550, 3600, 33 ]
    report = prep_report()
    epsilon = .0001
    rows = report["ROWS"]
    assert (rows[3]["I_MEAN"] - answers[0]) < epsilon, f"Wrong value for I_MEAN should be { 0.550}"
    assert rows[3]["PERIOD_SEC"] == answers[1], f"The period between measurements should be {3600}" 
    assert rows[3]["AH_USED"] == answers[2], f"AH_USED should be {33}"


def test_voltage_report_for_headers():
   answers=["SVR", "GUI", 101] 
   report = prep_report()
   assert report["SENDER"]==answers[0], f"SENDER Should be {SVR}"
   assert report["RECEIVER"]==answers[1], f"RECEIVER should be {GUI}"
   assert report["CODE"]==answers[2], f"CODE should be {101}"

#================= 
'''
# USAGE: in using module: from common/templates/adc_templates import ADC_T0_SVR_TEMPLATE

ADC_T0_SVR_TEMPLATE = 
{ "SENDER":"ADC",
  "RECEIVER":"SVR",
  "APP_ID":1,
  "VERSION":3,
  "MSGID": 123,
  "MEAS_ID":1,
  "TYPE":"m",
 "CHANS":[ 
               {"TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "DISCARD_SZ": 1 , "KEEP_SZ":63 , "A2D":[24500,24500]}, 
               {"TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "DISCARD_SZ": 1 , "KEEP_SZ":63 , "A2D":[24500,24500]},
               {"TIMESTAMP": 178000.0, "VIN":0 , "SAMP_SZ": 64, "DISCARD_SZ": 1 , "KEEP_SZ":63 , "A2D":[24500,24500]},
               {"TIMESTAMP": 178000.0, "I_MEAN":0.550,"PERIOD_SEC":3600, "AH_USED":0.550 },
            ]

}
'''
