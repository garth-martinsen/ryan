# file: gui_asyncio_client.py copied and adapted from  chatgpt_client.py
from collections import namedtuple
import asyncio
import json
import time

INCOMING_MSG = namedtuple("INCOMING_MSG", ("SENDER", "RECEIVER","TIMESTAMP", "MSGID", "CODE", "TYPE","CHAN","SAMP_SZ","DISCARD_SZ","KEEP_SZ","A2D_MEAN","VM_MEAN","VM_SD","VB","VIN","ERROR"))
OUTGOING_MSG = namedtuple("OUTGOING_MSG", ("SENDER", "RECEIVER","TIMESTAMP",  "CODE", "TYPE","CHAN","VIN"))
msg = 'GUI, ADC, 2026-5-20  17:40:27,  {code} , {atype} , {chan},  {vin} '  

#global vars

def _timestamp():
        """Returns local time as string, eg: YYYY-mm-DD HH:MM:SS. Note: for hour, min, sec less than 10, must have leading zero eg: 09:05:07"""
        return  time.time()
    
def human_timestamp(self, tm: float):
    ''' Returns human-readable string  eg: '2026-06-20 10:59:01' '''
    return datetime.datetime.fromtimestamp(tm).strftime('%Y-%m-%d %H:%M:%S')

def identify():
    msg = { "SENDER":"GUI", "CODE":0 }
    return msg

def get_msg():
    ''' Formats msg with cmd values to the Server'''
    print("include values for receiver, sender,  msgid, code, type, chan, vin as needed. If not needed just hit return with no entry eg: chan and vin ")
    ts = _timestamp()
    receiver = input("RECEIVER: " )
    sender = input("SENDER: " )
    code = int(input("CODE: " ))
    msg =  {"RECEIVER": receiver , "SENDER" : sender, "TIMESTAMP": ts, "CODE": code}
    if code == 175:
        msg["PERIOD" ]= int(input("period"))
        msg["REPS"]  =int( input("repetitions"))
    if code in [100,200]:
        msg["TYPE"] = input("type:" )
    if code == 200:
        msg["VIN"] = float(input("vin"))
        msg["CHAN"] = int(input("chan:" ))
    print(f" msg: {msg}")
    return msg  

async def tcp_client():
    reader, writer = await asyncio.open_connection( '192.168.254.19', 8888 )
    # send a hello msg to introduce me to the server
    hello = { "SENDER":"GUI", "CODE":0 }
    msg = json.dumps(hello) + "\n"
    writer.write(msg.encode())
    await writer.drain()
    
    #   the get_msg() emulates a GUI with user entering the values to be sent to the server.
    msg = get_msg()
    packet = json.dumps(msg) + "\n"
    writer.write(packet.encode())
    await writer.drain()

# acts when a msg is sent back to me from Server...
    data = await reader.readline()
    dataj = json.loads(data)
    print("Server responds with :", dataj)

    #writer.close()
    #await writer.wait_closed()

asyncio.run(tcp_client())
