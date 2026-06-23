# file: gui_asyncio_client.py copied and adapted from  chatgpt_client.py
from collections import namedtuple
import asyncio
import json
import time


INCOMING_MSG = namedtuple("INCOMING_MSG", ("SENDER", "RECEIVER","TIMESTAMP", "MSGID", "CODE", "TYPE","CHAN","SAMP_SZ","DISCARD_SZ","KEEP_SZ","A2D_MEAN","VM_MEAN","VM_SD","VB","VIN","ERROR"))
OUTGOING_MSG = namedtuple("OUTGOING_MSG", ("SENDER", "RECEIVER","TIMESTAMP",  "CODE", "TYPE","CHAN","VIN"))
msg = 'GUI, ADC, 2026-5-20  17:40:27,  {code} , {atype} , {chan},  {vin} '  

#global vars
funct_desc = {300: 'save_config(  msg : Config )',       310: 'get_config( chan : int )',
                        320:'save_to_bms( msg :BMS )' ,         330: 'list_bms( chan:int, atype:str) ',
                        340: 'get_bms_a2d_samples( bms_id : int)', 350: 'get_lut( chan:int)',
                        360: 'get_lut_timestamp( chan:int )',     370:'update_lut_pair(  _id:int,   vm:float,   vin:float)' ,
                        380: 'update_lut_timestamp( chan:int )', 390: 'get_vd_fracts( )'  }

def show_dbi_functions():
    for k,v in funct_desc.items():
        print(k,v)

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
    # print("Respond to promps. They will change depending on code (command). ")
    ts = _timestamp()
    receiver = input("RECEIVER: " )
    sender = "GUI" 
    code = int(input("CODE: " ))
    msg =  {"RECEIVER": receiver , "SENDER" : sender, "TIMESTAMP": ts, "CODE": code}
    msg["ARGLIST"]=[]
    if code == 175:
        msg["PERIOD" ]= int(input("period: "))
        msg["REPS"]  =int( input("repetitions: "))
    if code in [100,200]:
        msg["TYPE"] = input("type: " )
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
    # send a hello msg to introduce me to the server
    hello = { "SENDER":"GUI", "CODE":0 }
    msg = json.dumps(hello) + "\n"
    writer.write(msg.encode())
    await writer.drain()
    
    #   the get_msg() emulates a GUI with user entering the values to be sent to the server.
    # bug fixed: DONE the reader happens first, then another msg is created in get_msg() and sent out.
    while True:
        line = await reader.readline()   # blocks until reads "\n"
        dataj = json.loads(line)
        print("\tServer says :", dataj)
        
        msg = get_msg()
        packet = json.dumps(msg) + "\n"
        writer.write(packet.encode())
        await writer.drain()

    #writer.close()
    #await writer.wait_closed()
print(show_dbi_functions())
asyncio.run(tcp_client())
