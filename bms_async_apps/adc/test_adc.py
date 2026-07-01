# file: test_adc.py   ensure that adc is doing what the adc_asyncio_client is asking.
from adc import ADC
import asyncio
import time
import datetime



class TestAdc:
    def __init__(self, version):
        self.version = version
        self.adc = ADC(version)
        
    async def test_measure(self, msgid,  chan,  vin, purpose):
        #  async def measure(self, msgid, ch, vin, purpose):
        response = await self.adc.measure(msgid, chan, vin, purpose)
        print(f"prepared for svr: {response}")
        if chan == 0 and response["TYPE"] == 'm':
            response["VIN"] == 0.0
            
    async def test_set_rtc(self):
         # def set_rtc(self, ts: tpl):
         ''' Tests setting real time clock (rtc) by showing datetime "start",
            then setting datetime to "then",  and testing to see if it is changed correctly,
            then restoring to "start" and checking datetime for correctness.'''
         
         start = (2026, 6, 30, 1, 19, 25, 29, 45416)
         self.adc.rtc.datetime(start)
         start_result = self.adc.rtc.datetime()
         print(f"test starting datetime: {start_result}")
         then =(2000, 1, 1, 1, 0, 0,0, 0)
         self.adc.rtc.datetime(then)
         then_result = self.adc.rtc.datetime()
         print(f"then datetime : {then_result}")
         assert then_result[0]==2000
         assert then_result[1]==1
         assert then_result[2]==1
         #reset to original datetime
         self.adc.rtc.datetime(start)
         start_again_result = self.adc.rtc.datetime()
         assert start_again_result[0] == start[0], f"Year should be start.Year: {start[0]}, not: {start_again_result[0] }"
         assert start_again_result [4] == start[4] ,f"Hour should be start.Hour: {start[4]}, not: {start_again_result[4]}"
         print(f"start_again datetime : {start_again_result }")
         print()
         print("Passed test_set_rtc()")

        
# Tests
ta = TestAdc(3)

# asyncio.run(ta.test_measure( 5021,  0,  0.0, 100))
# asyncio.run(ta.test_measure( 5021,  1,  0.0, 100))
# asyncio.run(ta.test_measure( 5021,  2,  0.0, 100))
# asyncio.run(ta.test_measure( 5021,  0,  4.062, 200))
# asyncio.run(ta.test_measure( 5021,  1,  8.05, 200))
# asyncio.run(ta.test_measure( 5021,  2,  12.13, 200))
asyncio.run(ta.test_set_rtc())
