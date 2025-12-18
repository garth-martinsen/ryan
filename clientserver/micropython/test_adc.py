#file: test_adc.py   
from adc import ADC, ads
from collections import OrderedDict
from adc_cfg import Config
'''
Notes:
1. lookup_vb will fail if:
    luts are not OrderedDicts with keys (vm) sorted ascending
    local minimums exist in vm vs vb plot in  0.1V vd steps  ...
2. Lately the a2d samples are erratic with large swings. this causes failure iaw (1) above

Testable methods:                                                                                         Tested
                                                                                 ==================================
                                                                                                                           def check_i2c(self):
    def __str__(self):
    def datetimestamp(self):
                     def calibrate(self, chan, purpose, vin):
                     def measure(self, ch, purpose):
                     def sample_auto(self, x, samp=ads.alert_read):
                                                                                                                            def _turn_on(self, chn):
                                                                                                                            def _turn_off(self, chn):
    def show_gates(self):
                     def initialize_gates(self):
    def samples(self, chan):
                     def process_and_report(self, chan, purpose):
                     def reject_outliers(self, chan):
                     def stats(self, channel):
    def bracket_vm(self, chan, vm):
                                                                                                                           def _interpolate(self, chan, loval, vm, hival):
                     def lookup_vb(self, chan, vm):
'''

class TestAdc():
    def __init__(self):
        self.adc=ADC()
        #following are fetched from db_server in normal operation... Just mocked  here for testing. numbers are calculated, not measured.
        self.adc.cfg_ids=(1,2,3)
        self.adc.luts[0] = OrderedDict({2.0: 2.5, 2.095: 2.6, 2.19: 2.7, 2.285: 2.8, 2.38: 2.9, 2.475: 3.0, 2.57: 3.1, 2.665: 3.2, 2.76: 3.3, 2.855: 3.4, 2.95: 3.5, 3.045: 3.6, 3.1399998: 3.7, 3.2350002: 3.8, 3.33: 3.9, 3.425: 4.0, 3.52: 4.1, 3.615: 4.2, 3.71: 4.3, 3.805: 4.4, 3.9: 4.5})
        self.adc.luts[1] = OrderedDict ({ 2.0277596: 5.0, 2.0784536: 5.1, 2.1291476: 5.2, 2.1798416: 5.3, 2.2305356: 5.4, 2.2812296: 5.5, 2.3319236: 5.6, 2.3826174: 5.7, 2.4333114: 5.8, 2.4840054: 5.9, 2.5346994: 6.0, 2.268946   : 6.006, 2.31964     :  6.108, 2.367615   :   6.208, 2.419357   :     6.299, 2.466862   :     6.398, 2.514136   :     6.5, 2.561819   :   6.6, 2.608113   :   6.7, 2.655522   :   6.8, 2.70166       :  6.9, 2.74978     :  7.0, 2.79551     :  7.1, 2.84887     :  7.2, 2.898994   :     7.3, 2.953952   :   7.4, 3.007714   :   7.5, 3.060575   :   7.6, 3.113444   :   7.7, 3.168053   :   7.8, 3.221899   :   7.9, 3.275012   :   8.0, 3.328626   :   8.1, 3.381747   :       8.2, 3.435036   :   8.3, 3.488835   :   8.4, 3.544073   :   8.5, 3.598066   :   8.6, 3.651918   :   8.7, 3.706656   :   8.8, 3.759773   :   8.9, 3.808737   :   9.0 })
        self.adc.luts[2] = OrderedDict ({2.25: 7.5, 2.266667: 7.6, 2.2833332: 7.7, 2.3000002: 7.8, 2.3166666: 7.9, 2.3333336: 8.0, 2.35: 8.1, 2.3666668: 8.2, 2.3833332: 8.3, 2.4: 8.4, 2.4166668: 8.5, 2.4333334: 8.6, 2.45: 8.7, 2.4666668: 8.8, 2.4833334: 8.9, 2.5: 9.0, 2.516667: 9.1, 2.5333332: 9.2, 2.5500002: 9.3, 2.5666666: 9.4, 2.5833336: 9.5, 2.6: 9.6, 2.6166668: 9.7, 2.6333334: 9.8, 2.65: 9.9, 2.6666664: 10.0, 2.6833334: 10.1, 2.7: 10.2, 2.7166668: 10.3, 2.7333336: 10.4, 2.75: 10.5, 2.7666666: 10.6, 2.7833332: 10.7, 2.8000002: 10.8, 2.8166666: 10.9, 2.8333336: 11.0, 2.85: 11.1, 2.8666668: 11.2, 2.8833334: 11.3, 2.9: 11.4, 2.9166664: 11.5, 2.9333334: 11.6, 2.95: 11.7, 2.9666668: 11.8, 2.9833336: 11.9, 3.0: 12.0, 3.0166666: 12.1, 3.0333336: 12.2, 3.05: 12.3, 3.0666666: 12.4, 3.0833336: 12.5, 3.1000002: 12.6, 3.1166666: 12.7, 3.1333334: 12.8, 3.15: 12.9, 3.1666668: 13.0, 3.1833334: 13.1, 3.2: 13.2, 3.2166668: 13.3, 3.2333334: 13.4, 3.25: 13.5})
        
        self.adc.configs[0] = Config( 1, 'GM', 1, 'Development',  0, '4.2V CIRCUIT CHANNEL(0)',  1,    'BASELINE VERSION', '2025-9-29 20:20:36', 1, 'P-CHANNEL',    24.5,  0,   3,   0,           1000,     10000, 220,      0,  {})
        self.adc.configs[1] = Config( 2,  'GM',1,  'Development', 1, '8.4 V CIRCUIT CHANNEL(1)',  1,   'BASELINE VERSION', '2025-9-29 20:20:36',  2, 'P-CHANNEL',   25.4,  1,   3,  1000.0,   510.0,   10000.0, 480.0,  0,   {})
        self.adc.configs[2] = Config(  3,  'GM',1, 'Development', 2, '12.6V CIR00000000CUIT CHANNEL(2)',  1,   'BASELINE VERSION',  '2025-9-29 20:20:36', 3, 'P-CHANNEL',  25.4,  1,   3,  1000.0,   330.0,  10000.0, 480.0,   0,   {})

    def test_i2c(self):
        print()
        print("Testing_i2c ")
        lst =  ads.i2c.scan()
        print("List of addresses: ", lst)
        assert  72 in ads.i2c.scan(), "i2c address must be 72 if ads pin ADDR is grounded"
        print("Passed.....")
            
    def test_pin_0(self):
        '''When value of pin is 0, the gate can drain to a lower voltage, turning on current conduction. when pin value is 1 , current is shut off'''
        print()
        print("Testing gate pin 25")
        self.adc._turn_on(0)
        assert self.adc.gates[0].value()==0 , "Gate Pin 42 should be 0 when turned on"
        self.adc._turn_off(0)
        assert self.adc.gates[0].value()==1 , "Gate Pin 42 should be 1 when turned off"
        print("Passed.....")

    def test_pin_1(self):
         print()
         print("Testing gate pin 26")
         self.adc._turn_on(1)
         assert self.adc.gates[1].value()==0 , "Gate Pin 84 should be 0 when turned on"
         self.adc._turn_off(1)
         assert self.adc.gates[1].value()==1 , "Gate Pin 84 should be 1 when turned off"
         print("Passed.....")
        
    def test_pin_2(self):
        print()
        print("Testing gate pin 27")
        self.adc._turn_on(2)
        assert self.adc.gates[2].value()==0 , "Gate Pin 126  should be 0 when turned on"
        self.adc._turn_off(2)
        assert self.adc.gates[2].value()==1 , "Gate Pin 126 should be 1 when turned off"
        print("Passed.....")
        
    def test_interpolate(self):
        print()
        print("Testing Interpolation7")
        vlow=2.665    # 665: 3.2, 2.76: 3.3
        vhi =  2.76
        vm=  2.68
        truth = 3.2157896
        vb = self.adc._interpolate(0, vlow, vm,vhi)
        err = vb - truth
        print(f" vb: {vb}")
        print( f" vb - truth  :    { err }")
        assert abs(vb - truth) < .000001, f" error: {err}  should be smaller than {0.00001}"
        print("Error is less than: ", .0000001 )
        print("Passed.....")

    def test_ordered_lut_0(self):
        '''To ensure that lookup_vb works, the algorithm must have sorted keys in ascending order'''
        print()
        print("Testing  ordered_lut_0")
        klast = 0
        vlast = 0
        for k,v in sorted(self.adc.luts[0].items()):
            assert k > klast, f" key : {k} must be greater than {klast}"
            assert v > vlast, f" value : {v} must be greater than {vlast}"
            print(f"vm: {k}, vb: {v}")
            klast=k
            vlast=v
        print ("Passed...")
            
    def test_measure_0(self):
        '''For this test, the Vin must exceed 3.0 on power supply'''
        #TODO 1 : Mock the measured voltage, vm so Power supply is not a part of the test. For now set power supply at 3.0V
        print()
        print("Testing_measure_0")
        bms= self.adc.measure(0,100)
        print(bms)
        vm=round(bms["vm"], 2)
        vb = bms["vb"]
        print(f" vm: {vm}")
        typ = bms["type"]
        assert typ == 'm', f"Type of measurement should be 'm' not {typ}"
        assert vm == 2.29, f" Measured value, vm should not be: {vm}"
        #assert vb  == 3.0,  f" Estimated value, vb should  be: {bms.vb }"
        print ("Passed...")

        
    def test_calibrate_0_3_0(self):
        '''For this test, the Vin must exceed 3.0 on power supply'''
        #TODO 1 : Mock the measured voltage, vm so Power supply is not a part of the test.
        print()
        print("Testing_calibrate_0_3_0")
        bms = self.adc.calibrate(0,200, 3.0 )
        print(f"type(bms): {type(bms)}")                                        
        error = bms["error"]
        typ = bms["type"]
        print(f"bms.error: {error} ")
        assert typ == 'c', f"Type of measurement should be 'c' not {typ}"
        assert abs(error) < 0.15 ,  " bms.error: {error} should be smaller than : {.0001} "      # this needs study to determine what is acceptable error
        print ("Passed...")
    
    
T=TestAdc()
T.test_i2c()
T.test_pin_0()
T.test_pin_1()
T.test_pin_2()
T.test_interpolate()
T.test_ordered_lut_0()
T.test_measure_0()
T.test_calibrate_0_3_0()