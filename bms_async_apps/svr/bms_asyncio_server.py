# file: bms_asyncio_server.py   does not use websockets... uses asyncio tcp instead. works for µpython...
import asyncio
from collections import namedtuple
import json
import math
from common.bms_config import APP_ID, VERSION, SVR_IP, SVR_PORT
import common.secrets
from svr.database_interface import DatabaseInterface as DBI
from svr.svr_task_manager import SvrTaskManager
import time

#        BMS schema( id integer primary key, timestamp varchar, type varchar,chan integer,vin real, error real, a2d_mean integer, vm_mean real, vm_sd real, vb real);
BMS = namedtuple("BMS",("id","timestamp","msgid", "type","chan", "a2d_mean","vm_mean","vm_sd","vb","vin","error","samp_sz", "discard_sz","keep_sz"))
ADC= namedtuple("ADC", ("RECEIVER", "SENDER", "TIMESTAMP", "MSGID", "CODE", "TYPE","CHAN","VIN","SAMP_SZ", "SAMPLES"))
DB_TO_GUI_MSG=namedtuple("DB_TO_GUI_MSG",("RECEIVER", "SENDER", "ID", "TIMESTAMP", "MSGID", "CODE", "TYPE",
                                          "CHAN","A2D_MEAN","VM_MEAN","VM_SD","VB", "VIN","ERROR",
                          "SAMP_SZ", "DISCARD_SZ","KEEP_SZ"))
# ADC_CMDS = [2, 4, 10 ]
# DB_CMDS=[]
# DB_RSPNS= []
  
class Server:
    def __init__(self, app_id, version):
        self.app_id = APP_ID
        self.version = VERSION
        self.svr_task_manager= SvrTaskManager(APP_ID, VERSION)
        self.clients={}
        #print(f" self.__dict__ : {self.__dict__}")
        
    async def send_time_sync(self,requester):
        '''Send svr_tuple of time.gmtime() to requesting client'''
        tm = time.gmtime()
        #tm = time.localtime()
        msg={"SENDER": "SVR", "RECEIVER" : requester, "CODE" : 3, "ARGLIST": [tm]}
        await self.send_to_client(requester, msg)

    async def send_to_client(self, name, msg):
        '''Stringifies, adds newline, encodes, sends'''
        msgj= json.dumps(msg) +"\n"
        writer = self.clients[name]
        writer.write(msgj.encode())
        await writer.drain()

    async def handle_client(self,reader, writer):
        global k, vd_fracts, chan, lsb, vin
        addr = writer.get_extra_info('peername')
        print("Connected:", addr)
        
        try:
            while True:
                # block until receive a line with a "\n" ================
                line = await reader.readline()
                if not line:
                    print("Client disconnected")
                    break
                print("\tNew msg to svr, Received raw:", repr(line))
                try:
                    data = json.loads(line.decode())
                except ValueError as e:
                    print(f"Bad JSON: {e}")
                    continue
               
                print(f"\tServer Received MSG: type: {type(data)} ,  data: {data} ")
                # only stamp msgid on data that is going to ADC and then back to DBI... 
                if data["SENDER"]=="GUI" and data["RECEIVER"] == "ADC" :
                    msgid= svr_task_manager.dbi.next_msgid()
                    data["MSGID"]=msgid
                    #print(f" msgid stamped msg: {data}")
                code = data["CODE"]
                # capture and store the client writers when they send code=0 ,for later use
                #print(f"type(code) : {type(code)} , value: {code}")
                if code == 0:
                    if data["SENDER"] == "GUI" :
                        self.clients["GUI"] = writer
                    elif data["SENDER"] == "ADC" :
                        self.clients["ADC"] = writer
                    print(f"\tClients connected to this server: {len(self.clients)}")
                    i=0;
                    # List the clients that have registered with the svr.
                    for k,v in self.clients.items():
                        i+=1
                        print(i, k, v)
                    requester = data["SENDER"]
                    greeting = f"{requester}"
                    svr_to_client_msg = {"SENDER": "SVR", "RECEIVER" : requester, "CODE" : 1, "ARGLIST": [],  "WELCOME": greeting}  
                    print("Svr's registration response type & msg: ", type(svr_to_client_msg), svr_to_client_msg)
                    await self.send_to_client(requester, svr_to_client_msg)
                elif code == 2:
                    requester = data["SENDER"]
                    await self.send_time_sync(requester)
                else:
                    loop =asyncio.get_event_loop()
                    requester = data["SENDER"]
                    rspns_msg = await self.svr_task_manager.create_and_schedule_tasks( msg= data)
                    print("Response msg: ", rspns_msg)
                    await self.send_to_client( requester, rspns_msg)
        except Exception as e:
            print("Error:", e)
            print("file: " , e.__traceback__.tb_frame.f_code.co_filename)
            print("line no: " , e.__traceback__.tb_lineno)

        finally:
            writer.close()
            await writer.wait_closed()
            print("Disconnected:", addr)

async def main(app_id, version):
    svr = Server(APP_ID, VERSION)
    server = await asyncio.start_server( svr.handle_client,
        SVR_IP, SVR_PORT)
    print(f"Server is listening at: {SVR_IP} : {SVR_PORT}")

    async with server:
        await server.serve_forever()
    
    
asyncio.run(main(1,3))
