# file: bms_asyncio_server.py   does not use websocketa... uses asyncio tcp instead. works for µpython...
import asyncio
from collections import namedtuple
import json
import math
from common import bms_config
import common.secrets
from .database_interface import DatabaseInterface as DBI
#from adc_Interface import ADC_Interface as ADCIF
# from gui_interface import GUI_Interface as GUIIF
from .svr_task_manager import SvrTaskManager

#        BMS schema( id integer primary key, timestamp varchar, type varchar,chan integer,vin real, error real, a2d_mean integer, vm_mean real, vm_sd real, vb real);
BMS = namedtuple("BMS",("id","timestamp","msgid", "type","chan", "a2d_mean","vm_mean","vm_sd","vb","vin","error","samp_sz", "discard_sz","keep_sz"))
ADC= namedtuple("ADC", ("RECEIVER", "SENDER", "TIMESTAMP", "MSGID", "CODE", "TYPE","CHAN","VIN","SAMP_SZ", "SAMPLES"))
DB_TO_GUI_MSG=namedtuple("DB_TO_GUI_MSG",("RECEIVER", "SENDER", "ID", "TIMESTAMP", "MSGID", "CODE", "TYPE",
                                          "CHAN","A2D_MEAN","VM_MEAN","VM_SD","VB", "VIN","ERROR",
                          "SAMP_SZ", "DISCARD_SZ","KEEP_SZ"))
# ADC_CMDS = [30,32,40,42]
# DB_CMDS =  [4,10,12,20,22,50,52,54,60,62,64,66,70,72,74,76,78,80,82,90,92]
# DB_RSPNS=  [5,11,13,21,23,51,53,55,61,63,65,67,71,73,75,77,79,81,83,91,93] 
  
class Server:
    def __init__(self, app_id, version):
        self.app_id = app_id
        self.version = version
        self.svr_task_manager= SvrTaskManager(bms_config.APP_ID, bms_config.VERSION)
        self.clients={}
        print(f" self.__dict__ : {self.__dict__}")
        
    async def handle_client(self,reader, writer):
        global k, vd_fracts, chan, lsb, vin
        addr = writer.get_extra_info('peername')
        print("Connected:", addr)
        
        try:
            while True:
                
                line = await reader.readline()
                if not line:
                    print("Client disconnected")
                    break
                try:
                    data = json.loads(line.decode())
                except json.JSONDecodeError as e:
                    print(f"Bad JSON: {e}")
                    continue                    #if json is bad throw it away and wait for next \n terminated msg...
               
                print(f"\tServer Received MSG: type: {type(data)} ,  data: {data} ")
                code = data["CODE"]
                # capture and store the client writers when they send code=0 ,for svr_task_manager's use
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
                    sender = data["SENDER"]
                    greeting = f"{sender}"
                    svr_to_gui_msg = {"SENDER": "SVR", "RECEIVER" : sender, "CODE" : 1, "WELCOME": greeting}  
                    # response = f'Server says: hello {data["SENDER"]}, welcome!'
                    rspj=json.dumps(svr_to_gui_msg) + "\n"
                    writer.write(rspj.encode())
                    await writer.drain()
                else:    # with all clients registered, handle all non-zero codes in svr_task_manager...
                    loop =asyncio.get_event_loop()
                    rspns_msg = await self.svr_task_manager.create_and_schedule_tasks(loop=loop, clients= self.clients, msg= data)
        except Exception as e:
            print("Error:", e)
            print("file: " , e.__traceback__.tb_frame.f_code.co_filename)
            print("line no: " , e.__traceback__.tb_lineno)

        finally:
            writer.close()
            await writer.wait_closed()
            print("Disconnected:", addr)

async def main(app_id, version):
    svr = Server(app_id, version)
    server = await asyncio.start_server( svr.handle_client,
        bms_config.SVR_IP, bms_config.SVR_PORT)
    print(f"Server is listening at: {bms_config.SVR_IP} : {bms_config.SVR_PORT}")

    async with server:
        await server.serve_forever()
    
if __name__ == "__main__":
    asyncio.run(main(1,3))  # change app_id and version depending on app and version being used.
