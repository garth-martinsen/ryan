# file : phoney_gen.py   to generate msgs that look like a real namedtuple of the gui or the adc nodes...

from collections import namedtuple
import random
import math
import json
import time


# Constants
FSR= 4.096        # saved in Config db table
STEPS = 32768 # saved in Config db table
NOM = 21108     # adjust depending on Limits below for a channel.
ID_ADC = 1000   #increment from this for each originating adc msg. 
ID_GUI = 5000    #increment from this for each originating gui msg.
LSB = 4.096/32768   # computed in dbs using Config table values for FSR, STEPS


# LIMITS TO A2D for each channel
#chan 0: 16513 - 24769
#chan 1: 15033 - 17867
#chan 2: 17867 - 26801


class PhoneyGen:
    '''In the BMS, messages will be sent to the ESP32(adc) , the DatabaseServer (dbs), and the GUI Display(gui).
      Return msgs will be sent by adc to dbs. The dbs will notify the gui that a response is ready. The gui can rqst Config and LUTS from dbs.
      Codes for what is the purpose of the msg can be found in
      Google Doc at: https://docs.google.com/document/d/1mBtdG1vt6JvFzFWXOH9kK2mu5GbUy1_hcmY92V9aSNA/edit?tab=t.0.
      Tests for json at:chrome-extension://eifflpmocdbdmepbjaopkkhbfmdgijcc/index.html?options=%7B%22collapsed%22%3A0%2C%22css%22%3A%22%5Cn%2F**Write%20your%20CSS%20style%20**%2F%5Cn%23json-viewer%20%7B%5Cn%20%20%20%20font-size%3A%2015px%3B%5Cn%7D%5Cn%5Cn.property%7B%5Cn%20%20%20%20%2F*color%3A%23994c9e%3B*%2F%5Cn%7D%5Cn%5Cn.json-literal-numeric%7B%5Cn%20%20%20%20%2F*color%3A%23F5B041%3B*%2F%5Cn%7D%5Cn%5Cn.json-literal-url%20%7B%5Cn%20%20%20%20%2F*color%3A%20%2334a632%3B*%2F%5Cn%7D%5Cn%5Cn.json-literal-string%7B%5Cn%20%20%20%20%2F*color%3A%230642b0%3B*%2F%5Cn%7D%5Cn%5Cn.json-literal%7B%5Cn%20%20%20%20%2F*color%3A%23b568de%3B*%2F%5Cn%7D%5Cn%5Cn.json-literal-boolean%7B%5Cn%20%20%20%20%2F*color%3A%20%23f23ebb%3B*%2F%5Cn%7D%22%2C%22jsonDetection%22%3A%7B%22method%22%3A%22contentType%22%2C%22selectedContentTypes%22%3A%5B%22application%2Fjson%22%2C%22text%2Fjson%22%2C%22application%2Fjavascript%22%5D%7D%2C%22theme%22%3A%22default%22%7D#'''
    
    def next_adc_id(self):
        global ID_ADC
        ID_ADC = ID_ADC + 1
        return ID_ADC

    def next_gui_id(self):
        global ID_GUI
        ID_GUI = ID_GUI + 1
        return ID_GUI

    def timestamp(self):
        """Returns local time as string, eg: YYYY-mm-DD HH:MM:SS"""
        dt = time.localtime()
        return f"{dt[0]}-{dt[1]}-{dt[2]}_{dt[3]}:{dt[4]}:{dt[5]}"  # YYYY-MM-DD  HH:mm:sec (dt[6] dow , dt[7] julian)

    def gen_adc(self, frm, to, code, nom, chan, typ ):
        '''Returns a json.dumps of a json-worthy dict mimicing  ESP32  ADC action with phoney sample values.
          nom is a2d value around which to randomize, chan is one of [0,1,2], typ is "Type" one of ['m','c']'''
        
        ADC = namedtuple("ADC", ("frm", "to", "id", "code", "timestamp","chan","type","samples"))
        #generate phoney samples centered on nom and random varying by 3 counts in either direction...
        samps = []
        for s in range(0,64):
            samps.append(nom + random.randint(-3,3))
            
        adc=ADC(frm, to, self.next_adc_id(), code, self.timestamp(), chan, typ, samps)
        return json.dumps(adc._asdict())
        

    def gen_gui(self, frm,to,code, chan, vin):
        '''Returns a json-worthy dict mimicing a GUI msg requesting something from dbs or adc.'''
        GUI = namedtuple("GUI", ("frm", "to", "id", "code", "timestamp","chan", "vin"))
        gui = GUI(frm, to, self.next_gui_id(), code, self.timestamp(), chan, vin)
        #print("gui msg: " , json.dumps(gui._asdict()))
        return json.dumps(gui._asdict())
        
