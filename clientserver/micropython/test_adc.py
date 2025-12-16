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
        #following are fetched from db_server in normal operation... Just mocked  here for testing
        self.adc.cfg_ids=(1,2,3)
        self.adc.luts[0] = OrderedDict = ({ 2.386419 :   3.0 , 2.480494 :3.1 , 2.576982: 3.2 , 2.670677: 3.3 , 2.767054: 3.4 , 2.860863: 3.5 , 2.956999: 3.6 , 3.051115: 3.7 , 3.147765: 3.8 , 3.241461: 3.9 , 3.338363: 4.0 , 3.433948: 4.1 , 3.528541: 4.2 , 3.624836: 4.3 , 3.717937: 4.4 , 3.804493: 4.5 })
        self.adc.luts[1] = OrderedDict = ({ 2.268946   : 6.006, 2.31964     :  6.108, 2.367615   :   6.208, 2.419357   :     6.299, 2.466862   :     6.398, 2.514136   :     6.5, 2.561819   :   6.6, 2.608113   :   6.7, 2.655522   :   6.8, 2.70166       :  6.9, 2.74978     :  7.0, 2.79551     :  7.1, 2.84887     :  7.2, 2.898994   :     7.3, 2.953952   :   7.4, 3.007714   :   7.5, 3.060575   :   7.6, 3.113444   :   7.7, 3.168053   :   7.8, 3.221899   :   7.9, 3.275012   :   8.0, 3.328626   :   8.1, 3.381747   :       8.2, 3.435036   :   8.3, 3.488835   :   8.4, 3.544073   :   8.5, 3.598066   :   8.6, 3.651918   :   8.7, 3.706656   :   8.8, 3.759773   :   8.9, 3.808737   :   9.0 })
        self.adc.luts[2] = OrderedDict = ({ 2.85669   :   9.0, 2.8847   :   9.1, 2.9164   :   9.2, 2.9481   :   9.3, 2.9798  :    9.4, 3.0115  :      9.5, 3.0432  :      9.6, 3.0749  :      9.7, 3.1066  :      9.8, 3.1383  :      9.9, 3.17  :    10.0, 3.2017  :     10.1, 3.2334  :     10.2, 3.2651  :     10.3, 3.2968  :     10.4, 3.3285  :     10.5, 3.3602  :     10.6, 3.3919  :     10.7, 3.4236  :     10.8, 3.4553  :     10.9, 3.487   :   11.0, 3.5187  :   11.1, 3.5504  :     11.2, 3.5821  :     11.3, 3.6138  :     11.4, 3.6455  :     11.5, 3.6772  :     11.6, 3.7089  :     11.7, 3.7406  :     11.8, 3.7723  :     11.9, 3.804   :   12.0, 3.8357  :   12.1, 3.8674  :     12.2, 3.8991  :     12.3, 3.9308  :     12.4, 3.9625  :     12.5, 3.9942  :     12.6, 4.0259  :     12.7, 4.0627  :     12.8, 4.0893  :     12.9, 4.121   :   13.0, 4.1527  :   13.1, 4.1844  :     13.2, 4.2161  :     13.3, 4.2478  :     13.4, 4.2849  :     13.5 } )
        self.adc.configs[0] = Config( 1, 'GM', 1, 'Development',  0, '4.2V CIRCUIT CHANNEL(0)',  1,    'BASELINE VERSION', '2025-9-29 20:20:36', 1, 'P-CHANNEL',    24.5,  0,   3,   0,           1000,     10000, 220,      0,  {})
        self.adc.configs[1] = Config( 2,  'GM',1,  'Development', 1, '8.4 V CIRCUIT CHANNEL(1)',  1,   'BASELINE VERSION', '2025-9-29 20:20:36',  2, 'P-CHANNEL',   25.4,  1,   3,  1000.0,   510.0,   10000.0, 480.0,  0,   {})
        self.adc.configs[2] = Config(  3,  'GM',1, 'Development', 2, '12.6V CIRCUIT CHANNEL(2)',  1,   'BASELINE VERSION',  '2025-9-29 20:20:36', 3, 'P-CHANNEL',  25.4,  1,   3,  1000.0,   330.0,  10000.0, 480.0,   0,   {})

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
        print("Testing gate pin 27")
        self.adc._turn_on(2)
        assert self.adc.gates[2].value()==0 , "Gate Pin 126  should be 0 when turned on"
        self.adc._turn_off(2)
        assert self.adc.gates[2].value()==1 , "Gate Pin 126 should be 1 when turned off"
        print("Passed.....")
        
    def test_interpolate(self):
        print()
        print("Testing Interpolation7")
        vlow=2.576982
        vhi =  2.670677
        vm=  2.61
        truth = 3.23524
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
            print(f"Key: {k}, Value: {v}")
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

        
    def test_calibrate_0_3_6(self):
        '''For this test, the Vin must exceed 3.0 on power supply'''
        #TODO 1 : Mock the measured voltage, vm so Power supply is not a part of the test.
        print()
        print("Testing_calibrate_0_3_6")
        bms = self.adc.calibrate(0,200, 3.6 )
        print(f"type(bms): {type(bms)}")
        print(f" keys: {bms.keys()}")
        error = bms["error"]
        typ = bms["type"]
        print(f"bms.error: {error} ")
        assert typ == 'c', f"Type of measurement should be 'c' not {typ}"
        assert abs(error) < 0.15 ,  " bms.error: {error} should be smaller than : TBD "      # this needs study to determine what is acceptable error
        print ("Passed...")
    
    
T=TestAdc()
T.test_i2c()
T.test_pin_0()
T.test_pin_1()
T.test_pin_2()
T.test_interpolate()
T.test_ordered_lut_0()
T.test_measure_0()
T.test_calibrate_0_3_6()
               