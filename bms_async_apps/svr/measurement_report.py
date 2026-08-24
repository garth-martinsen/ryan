from common.templates.svr_templates import VOLTAGE_REPORT_TEMPLATE
from common.templates.adc_templates  import ADC_TO_SVR_TEMPLATE
from collections import OrderedDict
from services.discharge_curve import discharge_curve, Interpolator
from copy import deepcopy
import json

msg_to_gui = deepcopy(VOLTAGE_REPORT_TEMPLATE)
msg_from_adc = deepcopy(ADC_TO_SVR_TEMPLATE)

# constructor:  MeasurementReport( 0.0005, msg_to_gui) # Measurement class does not have a writer. Writer lives in SvrTaskMgr, so Measurements just reports back..

class MeasurementReport:
     '''Server helper class to return a msg(VOLTAGE_REPORT_TEMPLATE)  to gui with measurement report from ADC, augmented by svr_task_manager computations. '''
     def __init__(self, allowance, msg):
        self.allowance = allowance
        self.chans = OrderedDict({})
        self.interpolator = Interpolator()
        self.populate_from_adc(msg)
#        print(f"I am the MeasurementReport. I will predict Vb using::{discharge_curve} and fill in blanks in voltage_status_report  using template: {msg_to_gui} ")
#        print(f"my instance vars: {self.__dict__}")

#    def add_chan(self, chan_meas):
#       print(f"my instance vars: {self.__dict__}")
#        print(f"my instance vars: {self.__dict__}")
#        ch_meas = json.loads(chan_meas)
#        #print(f" ch_meas type is: {type(ch_meas)} ")
#        chan = ch_meas["CHAN"]
#        if ch_meas['MEAS_ID'] == self.meas_id:
#            self.chans[chan] = ch_meas

     def populate_from_adc(self, msg):
         '''Chans are: Voltage(0), Voltage(1), Voltage(2), Current(3). Their values come from chans:0,1,2,3 of ADC and computations on ADC.'''
         self.app_id=msg["APP_ID"]
         self.version = msg["VERSION"]
         self.msgid = msg["MSGID"]
         self.meas_id = msg["MEAS_ID"]
         self.type = msg["TYPE"]
         self.chans = msg["CHANS"]
         self.code = msg["CODE"]
         print(f"measurement_state : {self.__dict__} ") 


     def validate(self):
        valid = []
        amps_chan = self.chans[3]
        print(f"amps_chan : {amps_chan}")
        delta_time = amps_chan["TIMESTAMP"] - amps_chan["LAST_TIMESTAMP"]  # may need to do diff on two timestamps in more formal way.
        print(f"delta_time: {delta_time}")
        amp_hrs = amps_chan["AH_USED"]
        for i in range(3):
            chan = self.chans[i]
#            print(f"in validate: i : {i}, chan: {chan}")
            measured_vb = chan["VTAP"]
            if i-1 > -1:
                add_vb = self.chans[i-1]["VTAP"]
            else:
                add_vb = 0
            predicted_vb = self.interpolator.interpolate(amp_hrs)+ add_vb
            print(f"measured_vb : {measured_vb} predicted_vb : {predicted_vb} diff: {measured_vb-predicted_vb}")
            if abs(predicted_vb - measured_vb) < self.allowance :
                chan["reportable"] = 1
                valid.append(True)
                print(f"in validate(), valid list: {valid}")
            print("Channels to send to Gui:")
            for i in range(4):
                 print(self.chans[i])
        return sum(valid) == 3

     def format_and_return_report(self, msg_to_gui):
        '''Transfer values to the msg_to_gui object and return to SvrTaskMgr, which will send it.'''
        print(f"msg_to_gui TEMPLATE: {msg_to_gui}")  
        msg_to_gui["CODE"]= self.code
        msg_to_gui["MEAS_ID"]= self.meas_id

        rows = msg_to_gui["ROWS"]
        for i in range(3):
            print(f" in format_and_return_report() rows[{i}] : {rows[i]} ")
            print(f" in format_and_return_report() self.chans[{i}] : {self.chans[i]} ")
            rows[i]["ID_"]= self.chans[i]["ID_"]
            rows[i]["TIMESTAMP"] = self.chans[i]["TIMESTAMP"]
            rows[i]["TYPE"] = self.chans[i]["TYPE"]
            rows[i]["CHAN"] = i
            if i == 0:
                 rows[i]["VCELL"] = self.chans[i]["VTAP"]
            else:
                 rows[i]["VCELL"] = self.chans[i]["VTAP"] - self.chans[i-1]["VTAP"]
            rows[i]["VTAP"] =  self.chans[i]["VTAP"]
#        print(f" in format_and_return_report() rows[3] : {rows[3]} ")
#        print(f" in format_and_return_report() self.chans[{3}] : {self.chans[3]} ")
        rows[3]["ID_"] = self.chans[3]["ID_"]
        rows[3]["TIMESTAMP"]=self.chans[3]["TIMESTAMP"]
        rows[3]["I_MEAN"]=self.chans[3]["I_MEAN"]
        rows[3]["PERIOD_SEC"]=self.chans[3]["PERIOD_SEC"]
        rows[3]["AH_USED"]=self.chans[3]["AH_USED"]
        print(f" in format_and_return_report() msg_to_gui : {msg_to_gui} ")       
        return msg_to_gui

#==============================
'''
Sample msg from ADC:

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
 
sample msg from svr to gui:

VOLTAGE_REPORT_TEMPLATE = { "SENDER": "SVR", "RECEIVER": "GUI", "CODE": 101, "ROWS": [ 
    { "ID_": 1, "TIMESTAMP": 1783109112.0, "TYPE": "c", "CHAN": 0, "VCELL": 4.0323, "VTAP": 4.0323 }, 
    { "ID_": 2, "TIMESTAMP": 1783105513.0, "TYPE": "c", "CHAN": 1, "VCELL": 3.976, "VTAP": 7.999 } , 
    { "ID_": 3, "TIMESTAMP": 1783105513.0, "TYPE": "c", "CHAN": 2, "VCELL": 3.976, "VTAP": 11.999 } ,
    { "ID_": 4, "TIMESTAMP": 1783105513.0, "I_MEAN":0.22 , "PERIOD_SEC": 3600, "AH_USED": 0.22 } ] 
}

'''
