# file: chatgpt_client.py
from collections import namedtuple
import asyncio
import json

ADC= namedtuple("ADC", ("to", "frm","timestamp", "msgid", "code", "type","chan","vin","samp_sz", "samples"))
msg = 'DB, ADC, 2026-5-20  17:40:27, 5010, 201 , c , 2,  12.236 , 64, [21709, 21709, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24489, 24490, 24490, 24489, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24490, 24489, 24490, 24490, 24490] '

async def tcp_client():

    reader, writer = await asyncio.open_connection(
        '192.168.254.19',
        8888
    )

    #    writer.write(b'Hello Server')
    packet = json.dumps(msg) + "\n"
    writer.write(packet.encode())
    await writer.drain()

    data = await reader.readline()
#TODO 1: Find out why I cannot receive the msg sent from server until I control-C out of the server...
    print("Server Received, Processed, Stored, and Forwarded msg to me:", data)

    writer.close()
    await writer.wait_closed()

asyncio.run(tcp_client())