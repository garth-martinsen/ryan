# file: bms_asyncio_server.py   does not use websocketa... uses asyncio tcp instead. works for µpython...
import asyncio
from collections import namedtuple
import json
import math
from database_interface import DatabaseInterface as DBI
#from adc_Interface import ADC_Interface as ADCIF
# from gui_interface import GUI_Interface as GUIIF
from svr_task_manager import SvrTaskManager

#        BMS schema( id integer primary key, timestamp varchar, type varchar,chan integer,vin real, error real, a2d_mean integer, vm_mean real, vm_sd real, vb real);
BMS = namedtuple("BMS",("id","timestamp","msgid", "type","chan", "a2d_mean","vm_mean","vm_sd","vb","vin","error","samp_sz", "discard_sz","keep_sz"))
ADC= namedtuple("ADC", ("RECEIVER", "SENDER", "TIMESTAMP", "MSGID", "CODE", "TYPE","CHAN","VIN","SAMP_SZ", "SAMPLES"))
DB_TO_GUI_MSG=namedtuple("DB_TO_GUI_MSG",("RECEIVER", "SENDER", "ID", "TIMESTAMP", "MSGID", "CODE", "TYPE",
                                          "CHAN","A2D_MEAN","VM_MEAN","VM_SD","VB", "VIN","ERROR",
                          "SAMP_SZ", "DISCARD_SZ","KEEP_SZ"))
# ADC_CMDS = [100,175,200 ]
# DB_CMDS=[300,310, 312, 314, 350, 360, 362,364,370,372,374,372,374]
# DB_RSPNS= [311, 313,315, 361,363,365,371,373,375]
app_id=1
version=3
  
class Server:
    def __init__(self, app_id, version):
        self.app_id = app_id
        self.version = version
        self.svr_task_manager= SvrTaskManager(app_id, version)
        self.clients={}
        print(f" self.__dict__ : {self.__dict__}")
        
    async def handle_client(self,reader, writer):
        global k, vd_fracts, chan, lsb, vin
        addr = writer.get_extra_info('peername')
        print("Connected:", addr)
        
    # TODO 1: DONE. Figure out how to add both ADC and GUI  clients and have svr forward to ADC and to GUI when needed...
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
                    continue
               
                print(f"Received MSG: type: {type(data)} ,  data: {data} ")
                
                # capture and store the client writers when they send code=0 ,for later use
                if data["SENDER"]=="GUI":
                    msgid = self.svr_task_manager.dbi.next_msgid()
                    data["MSGID"]=msgid
                    print(f" msgid stamped msg: {data}")
                code = data["CODE"]
                #print(f"type(code) : {type(code)} , value: {code}")
                if code == 0:
                    if data["SENDER"] == "GUI" :
                        self.clients["GUI"] = writer
                    elif data["SENDER"] == "ADC" :
                        self.clients["ADC"] = writer
                    print(f"\tClients connected to this server: {len(self.clients)}")
                    i=0;
                    for k,v in self.clients.items():
                        i+=1
                        print(i, k, v)
                        
                    response = f'Server says: hello {data["SENDER"]}, welcome!'
                    rspj=json.dumps(response) + "\n"
                    writer.write(rspj.encode())
                    await writer.drain()
                else:
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

async def main(app_id, versiion):
    svr = Server(app_id, version)
    server = await asyncio.start_server( svr.handle_client,
        '192.168.254.19', 8888 )
    print("Server is listening on port 8888")

    async with server:
        await server.serve_forever()
    
    
asyncio.run(main(1,3))
