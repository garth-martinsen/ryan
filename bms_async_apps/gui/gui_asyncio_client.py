# file: gui_asyncio_client.py copied and adapted from  chatgpt_client.py
from collections import namedtuple, OrderedDict
import asyncio
import json
import time
from copy import deepcopy


INCOMING_MSG = namedtuple("INCOMING_MSG", ("SENDER", "RECEIVER","TIMESTAMP", "MSGID", "CODE", "TYPE","CHAN","SAMP_SZ","DISCARD_SZ","KEEP_SZ","A2D_MEAN","VM_MEAN","VM_SD","VB","VIN","ERROR"))
OUTGOING_MSG = namedtuple("OUTGOING_MSG", ("SENDER", "RECEIVER","TIMESTAMP",  "CODE", "TYPE","CHAN","VIN"))
msg = 'GUI, ADC, 2026-5-20  17:40:27,  {code} , {atype} , {chan},  {vin} '  

#global vars
funct_desc = OrderedDict({300: 'save_config(  msg : Config )', 302 : 'sync_time()',
                        310: 'get_config( chan : int )', 320: 'save_to_bms( msg :BMS )',
                        330: 'list_bms( chan:int, atype:str) ', 340: 'get_bms_a2d_samples( bms_id : int)',
                        350: 'get_lut( chan:int)', 352: 'get_lut_item(chan:int, vin:float)',
                        360: 'get_lut_timestamp( chan:int )', 370: 'update_lut_pair(  _id:int,   vm:float,   vin:float)',
                        380: 'update_lut_timestamp( chan:int )', 390: 'get_vd_fracts( )'})

# Flet will replace this Template dict and just make cmds as the User dictates... Timestamp will be set upon msg prep.
gui_cmd_templates = OrderedDict({
                         1: {'RECEIVER': 'ADC', 'SENDER': 'GUI', 'TIMESTAMP': 0.0,
                            'CODE': 302, 'ARGLIST': [] },
                        2: {'RECEIVER': 'ADC', 'SENDER': 'GUI', 'TIMESTAMP': 0.0,
                            'CODE': 100, 'ARGLIST': [], 'TYPE': 'm', 'VIN': 0.0},
                        3: {'RECEIVER': 'ADC', 'SENDER': 'GUI', 'TIMESTAMP': 0.0,
                            'CODE': 200, 'ARGLIST': [], 'VIN': 12.14, 'CHAN': 2},
                        4: {'RECEIVER': 'ADC', 'SENDER': 'GUI', 'TIMESTAMP': 0.0,
                            'CODE': 174, 'ARGLIST': [], 'PERIOD': 60, 'REPS': 5}, # 1 minute periods (60 seconds)
                        5: {'RECEIVER': 'ADC', 'SENDER': 'GUI', 'TIMESTAMP': 0.0,
                            'CODE': 274, 'ARGLIST': [], 'PERIOD': 60, 'REPS': 5, "VINS": [4.046,803,12.11]}})
# periodic example: for 3 days at 1/2 hour periods: period=1800 sec  reps=144
# periodic example:for 3 days at 1 hour period: period=3600 sec, reps =72 

def show_dbi_functions():
    for k,v in funct_desc.items():
        print(k,v)

# def _timestamp(self, tm):
#     """Returns local time as string, eg: YYYY-mm-DD HH:MM:SS"""
#     dt =time.localtime(tm)
#     return f"{dt[0]}-{dt[1]}-{dt[2]}  {dt[3]}:{dt[4]}:{dt[5]}"  # exclude day-of-week and julian date.

def _timestamp():
    ''' Returns a float eg: ... if this float is input to function human_timestamp( it will return a human readable string'''
    return time.time()
    
def human_timestamp( tm: float):
    ''' Returns human-readable string  eg: '2026-06-20 10:59:01' '''
    return time.localtime(tm).strftime('%Y-%m-%d %H:%M:%S')
    
async def receiver(reader):
    print("Receiver started")
    while True:
        line = await reader.readline()
        print("raw =", repr(line))
        if not line:
            print("SERVER CLOSED CONNECTION")
            break
        data = json.loads(line.decode())
        print("\tServer says:", data)

# TODO: The sender must be asyncio , python input statement blocks,  so they cannot be used.
# Flet will have to get the inputs without blocking...
# To emulate FLET, the following iterates thru all  gui_cmd_templates in gui_cmd_timplates dict. .
async def sender(writer):
    for template in gui_cmd_templates.values():
        msg = deepcopy(template)
        msg["TIMESTAMP"] = time.time()
        print("sending", msg)
        writer.write((json.dumps(msg) + "\n").encode())
        await writer.drain()
        await asyncio.sleep(1)
  
#     msg = deepcopy({'RECEIVER': 'ADC', 'SENDER': 'GUI', 'TIMESTAMP': 0.0,
#                             'CODE': 174, 'ARGLIST': [], 'PERIOD': 1800, 'REPS': 144}) # 3 days - every 1/2 hour
#     msg["TIMESTAMP"] = time.time()
#     print("sending", msg)
#     writer.write((json.dumps(msg) + "\n").encode())
#     await writer.drain()
#
#     msg = deepcopy({'RECEIVER': 'ADC', 'SENDER': 'GUI', 'TIMESTAMP': 0.0,
#                              'CODE': 302, 'ARGLIST': []}) #request for sync_time
#     msg["TIMESTAMP"] = time.time()
#     print("sending", msg)
#     writer.write((json.dumps(msg) + "\n").encode())
#     await writer.drain()


async def tcp_client():
    reader, writer = await asyncio.open_connection( '192.168.254.19', 8888 )

    # Register with the server first
    hello = { "SENDER":"GUI", "CODE":0 }
    
    writer.write((json.dumps(hello) + "\n").encode())
    await writer.drain()
    print("GUI registered with server")
   
    # now run forever 
    await asyncio.gather( receiver(reader), sender(writer))   

    #writer.close()
    #await writer.wait_closed()
   
   
print(show_dbi_functions())

asyncio.run(tcp_client())
