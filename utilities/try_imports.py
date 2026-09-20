from common.templates.adc_templates import ADC_T0_SVR_TEMPLATE
from common.templates.svr_templates import VOLTAGE_REPORT_TEMPLATE
from tests.test_data.ah_meter_test_data import START_TIME, END_TIME, VTAP, AMP_SUM, COUNT
from common.bms_config import APP_ID, VERSION
from copy import deepcopy
#from adc.adc import ADC

print()
print(f"voltage_report_template {VOLTAGE_REPORT_TEMPLATE}")
adc_msg_to_svr = deepcopy(ADC_T0_SVR_TEMPLATE)
#adc = ADC(APP_ID, VERSION)
print()
print(f"APP_ID : {APP_ID}, VERSION : {VERSION}")
print()
print(f"ADC_TO_SVR_TEMPLATE: {adc_msg_to_svr}")
#print(f"adc app: {adc}")
print()
print(f"test-data for ah_meter: START_TIME : {START_TIME}, END_TIME: {END_TIME} , VTAP: {VTAP}, AMP_SUM: {AMP_SUM}") 
#=====delete below this line==
'''
#start_time:time.localtime(1785601949.0)=time.struct_time(tm_year=2026,tm_mon=8,tm_mday=1,tm_hour=9,tm_min=32,tm_sec=29,tm_wday=5, tm_yday=213, tm_isdst=1)
START_TIME = 1785609149.00
#start_time:time.localtime(1785601949.0)=time.struct_time(tm_year=2026,tm_mon=8,tm_mday=1,tm_hour=10,tm_min=32,tm_sec=29,tm_wday=5, tm_yday=213, tm_isdst=1)
END_TIME = 1785612749.0
# Fully charged ...
VTAP = 12.6
# Mocked amp_sum, count
AMP_SUM = 13.2
COUNT = 60

'''
