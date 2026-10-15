import asyncio
from up.adc_client import AdcClient
ac= AdcClient()
asyncio.run(ac.start())
asyncio.run(ac.measure_volts({"CODE":30,"TYPE":'m', "MSGID": 156, "VINS": [0,0,0]}))
#asyncio.run(ac.start_periodic_voltage_measurements({"CODE":32,"TYPE":'m', "PERIOD":20, "REPS": 3, "MSGID": 156, "VINS": [0,0,0]}))
