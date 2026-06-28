# file: gui_asyncio_client.py copied and adapted from  chatgpt_client.py
from collections import namedtuple, OrderedDict
import asyncio
import json
import time


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
    return datetime.datetime.fromtimestamp(tm).strftime('%Y-%m-%d %H:%M:%S')

async def receiver(reader):
    print("Receiver started")
    while True:
        line = await reader.readline()
        print("raw =", repr(line))
        if not line:
            print("SERVER CLOSED CONNECTION")
            break
        data = json.loads(line.decode())
        print("Server says:", data)
        
async def sender(writer):
    while True:
        msg = await get_msg()

        writer.write((json.dumps(msg)+"\n").encode())
        await writer.drain()
        
async def get_msg():
    ''' Formats msg with cmd values to the Server'''
    # print("Respond to promps. They will change depending on code (command). ")
    ts = _timestamp()
    receiver = input("RECEIVER: " )
    sender = 'GUI'
    code = int(input("CODE: " ))
    msg =  {"RECEIVER": receiver , "SENDER" : sender, "TIMESTAMP": ts, "CODE": code}
    msg["ARGLIST"]=[]
    if code == 1:
        print(msg)
    if code == 175:
        msg["PERIOD" ]= int(input("period: "))
        msg["REPS"]  =int( input("repetitions: "))
    if code  == 100:
        msg["TYPE"] = input("type: " )
        msg["VIN"] = 0.0
    if code == 200:
        msg["VIN"] = float(input("vin: "))
        msg["CHAN"] = int(input("chan: " ))
    if code in [ 300,310,320, 330, 340, 350, 360, 370]:
        for k, v in funct_desc.items():
            print(k,v)
            
        msg["ARGLIST"] = json.loads(input("arglist: "))      #input returns a stringified list . needs to be a list
        
    print(f"\tGUI client sending msg: {msg}")
    return msg  

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
