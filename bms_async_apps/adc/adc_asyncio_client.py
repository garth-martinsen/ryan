# file: adc_asyncio_client.py
from common  import bms_config 
from collections import namedtuple
from adc import ADC
import asyncio
import json
from machine import RTC

# print("Imported from bms_config the following:")
# print("APP_ID: ", bms_config.APP_ID)
# print("VERSION: ", bms_config.VERSION)
# print("SVR_IP:", bms_config.SVR_IP)
# print("SVR_PORT: ", bms_config.SVR_PORT)
# print("VINS: ", bms_config.VINS)


#global variables...
adc =  ADC(bms_config.VERSION)
reps=0
reps_done=0
period =0

async def route_msg( msg, writer):
    
    global reps, reps_done
    cmd = msg["CODE"]
    msgid = msg.get("MSGID")   
    print(f" cmd: {cmd}  msgid: {msgid}  ")
    if cmd == 1:
        print(msg)
    if cmd == 100:
        for chan in range(3):
            vin = 0.0
            response = await adc.measure(msgid, chan,vin, cmd)
            response["CODE"]=101
            respj = json.dumps(response) +"\n"
            writer.write(respj.encode())
            await writer.drain()

    if cmd == 200:
        args = msg["ARGLIST"]
        print("args: ", args)
        vins=args[0]
        for chan in range(3):
            vin = vins[chan]
            response = await adc.measure(msgid, chan,vin, cmd)
            respj = json.dumps(response) +"\n"
            writer.write(respj.encode())
            await writer.drain()
            
    # start periodic measurements...        
    elif cmd == 174:
        ''' Gets period and reps from msg, then in nested for loops, measures and sends for ea chan.
           Then asyncio.sleeps for period seconds, then repeats until all of the reps are done.'''
        # periodic measurements are just measures (100) so use cmd = 100
        cmd=100
        period = msg["PERIOD"]
        reps = msg["REPS"]
        print(f"ADC responding to the 174 cmd (start_periodic_measurements for period: {period} seconds and reps: {reps}")
        reps = reps
        reps_done = 0
        vin = 0.0     #  for a measurement  vin=0.0 , but vin is passed in for a calibration
        for cnt in range(reps):
            for chan in range(3):
                response = await adc.measure( msgid, chan,vin, cmd)
                writer.write((json.dumps(response) +"\n").encode())
                await writer.drain()
                await asyncio.sleep(period)
                reps_done  += 1
                print(f"\tFor command 174 reps_done: {reps_done} of requested reps: {reps}")
        print(f"All {reps} repetitions were completed in start_periodic_measurements (174) cmd")
    # many repeated calibrations, same as 174 except type='c' and vin is the truth value.   
   
    elif cmd == 274:
        # repeated 200 cmd reps times so set cmd to 200 for each call to measure.
        cmd=200
        period = msg["PERIOD"]
        reps = msg["REPS"]
        vins = msg["VINS"]
        print(f"ADC responding to the 274 cmd (start_periodic_measurements for period: {period} seconds and reps: {reps}")
        reps = reps
        reps_done = 0

        for cnt in range(reps):
            for chan in range(3):
                response = await adc.measure( msgid, chan,vins[chan], cmd)
                writer.write((json.dumps(response) +"\n").encode())
                await writer.drain()
                await asyncio.sleep(period)
            reps_done  += 1
            print(f"\tFor cmd: 274  the reps_done: {reps_done} of requested reps: {reps}")
        print(f"\tAll {reps} repetitions were completed in start_periodic_calibrations (274) cmd")

#TODO 3: Finish/DEBUG block  303 for rtc time setting;
      
    elif cmd == 303:
        print(f"msg: {msg}")
        time = msg["TIME_SYNC"]
        response =adc.set_rtc(time)
        response = json.dumps(response)+"\n"
        print(f"ADC response to SVR: {response}")
        writer.write(response.encode())
        await writer.drain()
        
        
async def tcp_client():
    print(f"Starting tcp_client with svr_ip: {bms_config.SVR_IP} , svr_port: {bms_config.SVR_PORT} ")
    reader, writer = await asyncio.open_connection( bms_config.SVR_IP, bms_config.SVR_PORT)
    # send a hello msg to introduce me to the server
    hello = { "SENDER":"ADC", "CODE":0 }
    msg = json.dumps(hello) + "\n"
    writer.write(msg.encode())
    await writer.drain()
    #request time_sync
    print("Requesting time_sync from SVR...")
    time_sync = {"SENDER":"ADC", "CODE":302, "ARGLIST": [], "MSGID": 0}
    writer.write((json.dumps(time_sync) + "\n").encode())
    writer.drain() 
    while True:
        print("ADC waiting for server message")
        line = await reader.readline()   # blocks until reads a "\n"
#         print("ADC raw line:", repr(line))
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
        
    
®
    #TODO : Rule to send out msg :  1. msgj=json.dumps(msg) + "\n" -> 2. writer.write(msgj.encode()) -> 3. await writerrain()
    #     packet = json.dumps(msg) + "\n"
    #     writer.write(packet.encode())
    #     await writer.drain()
