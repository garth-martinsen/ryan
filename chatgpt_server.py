# file: chatgpt_server.py   does not use websocketa... uses asyncio tcp instead. works for µpython...
import asyncio
from collections import namedtuple
import json
import math
# from  database_interface import DBI

      #BMS schema( id integer primary key, timestamp varchar, type varchar,chan integer,vin real, error real, a2d_mean integer, vm_mean real, vm_sd real, vb real);
BMS = namedtuple("BMS",("id","timestamp","msgid", "type","chan", "a2d_mean","vm_mean","vm_sd","vb","vin","error","samp_sz", "discard_sz","keep_sz"))
ADC= namedtuple("ADC", ("to", "frm", "timestamp", "msgid", "code", "type","chan","vin","samp_sz"))
DB_TO_GUI_MSG=namedtuple("DB_TO_GUI_MSG",("to", "frm", "id", "timestamp", "msgid", "code", "type","chan","a2d_mean","vm_mean","vm_sd","vb", "vin","error",
                          "samp_sz", "discard_sz","keep_sz"))
# the following three variables will be fetched from db Config and injected into server constructor.
lsb = 125e-6
vd_fracts=[0.749814585908529, 0.33633904418395, 0.250186335403727]
k = 2.0

def get_config_from_db(self):
        '''TBD '''
        print("Not yet implemented..")
        return (lsb, vd_fracts, k)
    
#dbi = DBI(1,3)
  
class Server:
    def __init__(self, lsb, vd_fracts, k):
#    def __init__(dbi):
        #self.dbi=dbi
        #self.cfg[0] =dbi.get_config(0)
        #self.FSR= self.cfg[0].ADC_FSR
        #self.steps = self.cfg[0].ADC_STEPS
        self.lsb = lsb
        self.k = k
        self.vd_fracts = vd_fracts
        
    def  store_in_db(self, bms, samples):
        '''This will be moved to DBI or to best place...'''
        print(f"TBD: insert into BMS table: {bms}")
        bms_id=23
        print(f" insert into A2D table:  values(NULL, {bms_id}, {samples})")

    def return_to_GUI(self, bms):
       # let bms["id"] = 23 .  the database table will assign the correct id number to the record. Just putting phoney number here
       
        msg = DB_TO_GUI_MSG("GUI", "DBS", 23, bms.timestamp, bms.msgid, 201, bms.type, bms.chan, bms.a2d_mean, bms.vm_mean, bms.vm_sd,
                           bms.vb, bms.vin, bms.error, bms.samp_sz, bms.discard_sz, bms.keep_sz)
        print(f" send to GUI: {msg}")

    def translate_client_msg(self, data):
        b1=data.index('[')
        s=data[b1+1: -2]
        samples= [int(x) for x in s.split(",")]    # list of ints that are a2d samples
        fields=data.split(",")[0:9]
        print("fields: ", fields)
        adc = ADC(*fields)
        #print("samples: ", samples)
        #print("adc: ", adc)
        #print("Extracting chan and vin")
        chan = int(adc.chan)
        vin = adc.vin
        return  adc, samples,chan

    def avg(self, samps):
        '''used to compute mean and sd.'''
        return sum(samps)/len(samps)

#TOO 2: call dbi to perform this and get rid of this method.
    def compute(self, samples, lsb, k, vd_fract, vin ):
        print(f"entered Server compute function with: the samples ,{lsb}, {k} ,{vd_fract},  {vin }")
        samp_sz=len(samples)
        vin = float(vin)
        m=self.avg(samples)
        #print("hw1")
        vrs = [(x-m)*(x-m) for x in samples]
        sd = math.sqrt(self.avg(vrs))
        #print("hw2")
        #discard outliers... may need to adjust k . To start, pass in k=3
        keep = [x for x in samples if abs(x-m) < (sd*k)]
        #print("hw3")
        # final pass: do stats on keep in liew of samples
        keep_sz=len(keep)
        discard_sz = samp_sz - keep_sz
        print(f"keep_sz: {keep_sz}  discard: {len(samples)- keep_sz}")
       #print("hw4")
        m = round(self.avg(keep), 4)
        vrs =  [(x-m)*(x-m) for x in keep]
        sd = math.sqrt(self.avg(vrs))
        vm= round(m*lsb, 4)
        #print("hw5")
        vm_sd=round(sd*lsb, 8)
        vb = round(vm/vd_fract, 4)
        #print(f"hw6  vb: {vb} vin: {vin} type(vin): {type(vin)}")
        error = round((float(vin) - vb), 6)
        #print("hw7")
        return m, vm, vm_sd, vb, error, samp_sz, discard_sz, keep_sz

    async def handle_client(self,reader, writer):
        global k, vd_fracts, chan, lsb, vin
        addr = writer.get_extra_info('peername')
        print("Connected:", addr)
    # TODO 1: Figure out how to add both ADC and GUI  clients and have svr forward to ADC and to GUI when needed...
        try:
            while True:
                
                line = await reader.readline()
                data = json.loads(line)

                if not data:
                    break

                print("Received:", data)
                adc, samples, chan = self.translate_client_msg(data)
                vin = float(adc.vin)
                #   return m, vm, vm_sd, vb, error, samp_sz, discard_sz, keep_sz
                m, vm, vm_sd, vb, error, samp_sz, discard_sz, keep_sz = self.compute(samples, lsb, k,  vd_fracts[chan], vin)
                print(f" a2d_mean: {m}, vm_mean: {vm}, vm_sd: {vm_sd},  vb: {vb}, vin: {vin}, err: {error}")
                bms=BMS("NULL", adc.timestamp, adc.msgid.strip(), adc.type.strip(),chan, m, vm, vm_sd, vb,  vin, error, samp_sz, discard_sz, keep_sz)
                self.store_in_db(bms, samples)
                
                #return_to_GUI(bms)
                msg = DB_TO_GUI_MSG("GUI", "DBS", 23, bms.timestamp, bms.msgid, 201, bms.type, bms.chan, bms.a2d_mean, bms.vm_mean, bms.vm_sd,
                               bms.vb, bms.vin, bms.error, bms.samp_sz, bms.discard_sz, bms.keep_sz)
        
                #tag = f"msgid :{adc.msgid.strip()}_{adc.timestamp }\n"
                msgj=json.dumps(msg)
                print("msgj: ", msgj)
                writer.write(msgj.encode())
                await writer.drain()

        except Exception as e:
            print("Error:", e)

        finally:
            writer.close()
            await writer.wait_closed()
            print("Disconnected:", addr)

async def main():
    svr = Server(lsb, vd_fracts, k)
    server = await asyncio.start_server(
        svr.handle_client,
        '0.0.0.0',
        8888 )
    print("Server is listening on port 8888")

    async with server:
        await server.serve_forever()
    
    
asyncio.run(main())