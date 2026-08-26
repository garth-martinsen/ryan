# file: adc_asyncio_client.py

from common.bms_config import APP_ID, VERSION
from common.templates.adc_templates import ADC_TO_SVR_TEMPLATE
import asyncio
import json
from machine import RTC
import math


# print("Imported from bms_config the following:")
# print("APP_ID: ", bms_config.APP_ID)
# print("VERSION: ", bms_config.VERSION)
# print("SVR_IP:", bms_config.SVR_IP)
# print("SVR_PORT: ", bms_config.SVR_PORT)
# print("VINS: ", bms_config.VINS)


# Create the two global instances that will obey adc_asyncio_client
adc = ADC(APP_ID,VERSION)
ahmeter=AhMeter(vtap, lsb, rs, amp_gain )     # created here, used in every voltage measurment cycle.
reps=0
reps_done=0
period =0
rtc=RTC()

async def send(msg:dict, writer):
    '''adc_asyncio_client sends all msgs from adc objects . Precondition: msg contains all required fields. No changing once you get here.'''
    respj = json.dumps(msg) +"\n"
    writer.write(respj.encode())
    await writer.drain()
    return True

async def start_periodic_current_measurements(msg: dict):
    '''Setup the periodic current measurements from the battery's highest Vtap (cfg.PACK_VOLTS). 
       global adc, ahmeter
       Measurments will reset and restart accumulating right after a voltage_report is sent to the SVR...
       The assumption is made that amp_measurments will be made many times during a volt_meas_period so reps is not used...'''
    vtap = msg["VTAP"]
    amps_chan = 3         # All current measurements will be saved in chan[3] part of RAM using cfg.ADC_AMPS_FSR (1.024) V.
    fsr = msg["ADC_AMPS_FSR"]
    current_meas_period = msg["ADC_AMP_MEAS_PERIOD"]
    ahmeter.reset()
    ahmeter.start(vtap,rtc.datetime())
    while not adc.reporting:               # when adc is preparing a voltage report, it sets 'adc.reporting' causing this loop to exit.
        await adc.measure(amps_chan)
        await ah_meter.accumulate()        #ah_meter knows where to get the a2d samples and it processes them and calls its method: add_amps(...)
        asyncio.sleep(current_meas_period)

async def start_periodic_voltage_measurements(msg:dict, ah_meter, writer):
    '''asyncio method. No need to stop measurements because they are ~ 1 hour apart. It will take micro_seconds to report_to_server...'''
    global adc, ahmeter
    volt_meas_period = float(msg["ADC_VOLT_MEAS_PERIOD"])
    reps = int(["REPS"] )
    if reps == 0:
        reps =int(math.pow(2, 32)) 
    # get fields needed to pass back to the SVR.
    msgid = msg["MSGID"]
    code = msg["CODE"]
    if code in [200, 274]:
        vins = msg["VINS"]
    else:
        vins = [0,0,0]
    fsr = float(msg["ADC_VOLT_FSR"])
    # get the amps measurements and accumulation under way...
    for rep in reps: 
       start_periodic_current_measurements(msg)
       for chan in range(3):
           await adc.measure(chan)
       if prepare_and_send_report(writer) :
           reps_done += 1
           print(f"\tFor command {code} reps_done: {reps_done} of requested reps: {reps}")
       break
       print(f"All {reps} repetitions were completed in start_periodic_measurements cmd")
       #TODO 4: Try to use: single_voltage_measurement(...)  in :  start_periodic_voltage_measurements(...) can be shorter...

async def single_voltage_measurement(msg:dict, ah_meter, writer):
    '''Create and send a report for a single-shot measurement request. Try to re-use this so start_periodic_voltage is shorter...  '''
    global adc, ahmeter
    # get fields needed to pass back to the SVR.
    msgid = msg["MSGID"]
    code = msg["CODE"]
    fsr = msg["ADC_VOLT_FSR"]     # not used for now...    
    if code in [200, 274]:
        vins = msg["VINS"]
    else:
        vins=[0,0,0]
    start_periodic_current_measurements(msg)
    for chan in range(3):
        await adc.measure(chan)
        if prepare_and_send_report(writer):
            break

async def prepare_and_send_report(writer):        
    '''Deep copies the ADC_T0_SVR_TEMPLATE as report_msg.  ah_meter and adc populates their parts of report_msg,then calls send(...) and returns boolean.'''
    global adc, ahmeter
    report_msg = deepcopy(ADC_T0_SVR_TEMPLATE)
    await  ah_meter.report_to_svr(report_msg)    
    await adc.report_to_svr(report_msg, msgId, vins)    # adc will create next meas_id when creating the report.
    return send(adc_report, writer) 


async def route_msg( msg, writer):
    
    global reps, reps_done, adc, ahmeter
    cmd = msg["CODE"]
    msgid = msg.get("MSGID")   
    print(f" cmd: {cmd}  msgid: {msgid}  ")
    if cmd == 1:
        print(msg) 
    if cmd in  [100, 200]:
        single_voltage_measurement(msg, ah_meter, writer)
    elif cmd in [ 174, 274]:
        """Extracts period and reps from msg, then in for loop, measures and sends report for all chans (including amps_chan)""" 
        start_periodic_voltage_measurements(msg, ah_meter, writer)
        reps_done  += 1
        print(f"\tFor command 174 reps_done: {reps_done} of requested reps: {reps}")
        print(f"All {reps} repetitions were completed in start_periodic_calibrations ({cmd}) cmd")

    #TODO 3: Finish/DEBUG block  303 for rtc time setting;
    elif cmd == 303:
        print(f"msg: {msg}")
        time = msg["TIME_SYNC"]
        response =adc.set_rtc(time)
        response = json.dumps(response)+"\n"
        print(f"ADC response to SVR: {response}")
        writer.write(response.encode())
        await writer.drain()
        
    elif cmd == 305:
        # set the starting meas_id on the adc. It will autoincrement by 1 thereafter.
        print(f"msg: {msg}")
        adc.meas_id = msg["MEAS_ID"]
        
async def tcp_client():
    global adc, ahmeter
    print(f"Starting tcp_client with svr_ip: {bms_config.SVR_IP} , svr_port: {bms_config.SVR_PORT} ")
    reader, writer = await asyncio.open_connection( bms_config.SVR_IP, bms_config.SVR_PORT)

    #1. send a hello msg to introduce me to the server
    hello = { "SENDER":"ADC", "CODE":0 }
    send(hello, writer)

    #2.request time_sync
    print("Requesting time_sync from SVR...")
    time_sync = {"SENDER":"ADC", "CODE":302, "ARGLIST": [], "MSGID": 0}
    send(time_sync, writer)

    #3.request max meas_id in bms table
    max_meas_id = {"SENDER":"ADC", "CODE": 304, "ARGLIST": []}
    send(max_meas_id, writer) 

    while True:
        print("ADC waiting for server message")
        line = await reader.readline()   # blocks until reads a "\n"
        #print("ADC raw line:", repr(line))
        msg=json.loads(line.decode())
        print("\tADC decoded msg:", msg)
        #print(f"writer: {writer}  msg: {msg}")
        if not isinstance(msg, dict):
            print("Ignoring non-command message:", msg)
            continue
        await route_msg(msg, writer)
        
 
    #TODO 2: ask chatgpt how to place following two lines.  For now, just comment them out...
    #             writer.close()
    #             await writer.wait_closed()
    

asyncio.run(tcp_client())
        
#TODO : Rule to send out msg :  1. msgj=json.dumps(msg) + "\n" -> 2. writer.write(msgj.encode()) -> 3. await writer.drain()
#     packet = json.dumps(msg) + "\n"
#     writer.write(packet.encode())
#     await writer.drain()

