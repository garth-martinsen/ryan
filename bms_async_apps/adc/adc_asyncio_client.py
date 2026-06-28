# file: adc_asyncio_client.py

from collections import namedtuple
from adc import ADC
import asyncio
import json
from machine import RTC
version = 3

adc =  ADC(version)

svr_ip =  '192.168.254.19',
svr_port =8888

async def route_msg( msg, writer):
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
        chan = msg["CHAN"]
        vin = msg["VIN"]
        response = await adc.measure(msgid, chan,vin, cmd)
        respj = json.dumps(response) +"\n"
        writer.write(respj.encode())
        await writer.drain()
            
    elif cmd == 175:
        period = msg["PERIOD"]
        reps = msg["REPS"]
        adc.start_periodic_measurements( msgid, period, reps)
        response = {"SENDER": "ADC" , "RECEIVER": "SVR", "MSGID": msgid, "REPLY": "Periodic Measurements Started"}
        respj = json.dumps(response) +"\n"
        writer.write(respj.encode())
        await writer.drain()

#TODO 3: Finish/DEBUG block  302 for rtc time setting;
      
    elif cmd == 302:
        print(f"msg: {msg}")
        time = msg["TIME"]
        adc.set_rtc(time)

async def tcp_client():   
    reader, writer = await asyncio.open_connection( '192.168.254.19', 8888)
    # send a hello msg to introduce me to the server
    hello = { "SENDER":"ADC", "CODE":0 }
    msg = json.dumps(hello) + "\n"
    writer.write(msg.encode())
    await writer.drain()
    msg=""
    while True:
        print("ADC waiting for server message")
        line = await reader.readline()   # blocks until reads a "\n"
        #print("ADC raw line:", repr(line))
        msg=json.loads(line.decode())
        print("\tADC decoded msg:", msg)
        #TODO 1: do : from adc import ADC;   wire it up so I can: 1. call adc.measure(c) where c=chan [0,1,2]; 2. call adc.start_periodic(period, reps).
        #print(f"writer: {writer}  msg: {msg}")
        if not isinstance(msg, dict):
            print("Ignoring non-command message:", msg)
            continue
        await route_msg(msg, writer)
        
    
    #TODO 2: ask chatgpt how to place following two lines.  For now, just comment them out...
    #             writer.close()
    #             await writer.wait_closed()
    

asyncio.run(tcp_client())
        
            
#         elif cmd == 302:
#             print(f"msg: {msg}")
#             time = msg["TIME"]
#             adc.set_rtc(time)

        
      




    #TODO : Rule to send out msg :  1. msgj=json.dumps(msg) + "\n" -> 2. writer.write(msgj.encode() -> 3. await writer.drain()
    #     packet = json.dumps(msg) + "\n"
    #     writer.write(packet.encode())
    #     await writer.drain()