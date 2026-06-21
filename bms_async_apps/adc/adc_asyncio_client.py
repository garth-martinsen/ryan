# file: adc_asyncio_client.py
from collections import namedtuple
import asyncio
import json

# phoney data so I can build the software...
samples = [21709, 21709, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24489, 24490, 24490, 24489, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24489, 24490, 24490, 24490]
ADC= namedtuple("ADC", ("RECEIVER", "SENDER","TIMESTAMP", "MSGID", "CODE", "TYPE","CHAN","VIN","SAMP_SZ", "SAMPLES"))
STD_MSG =namedtuple("STD_MSG", ("RECEIVER", "SENDER", "TIMESTAMP", "MSGID", "CODE", "TYPE", "CHAN", "VIN"))
msg = { "RECEIVER": "DB","SENDER" : "ADC", "TIMESTAMP" : '2026-5-20  17:40:27',  "CODE" : 201 , "TYPE" : 'c' , "CHAN" : 2,  "VIN" : 12.236 , "SAMP_SZ" : 64, "SAMPLES" : samples }

async def tcp_client():

    reader, writer = await asyncio.open_connection( '192.168.254.19', 8888 )
 # send a hello msg to introduce me to the server
    hello = { "SENDER":"ADC", "CODE":0 }
    msg = json.dumps(hello) + "\n"
    writer.write(msg.encode())
    await writer.drain()
    
    #todo : Rule to send out msg :  1. msgj=json.dumps(msg) + "\n" -> 2. writer.write(msgj.encode() -> 3. await writer.drain()
        #     packet = json.dumps(msg) + "\n"
        #     writer.write(packet.encode())
        #     await writer.drain()

    data = await reader.readline()   # blocks until reads a "\n"
    dataj=json.loads(data.decode())
    print(f"  {dataj}")

    writer.close()
    await writer.wait_closed()

asyncio.run(tcp_client())