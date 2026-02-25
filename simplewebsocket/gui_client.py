# file: gui_client.py
import asyncio
import websockets
from client_data_store import DataStore as DS

class GUIClient:
    def __init__(self, db_uri, adc_uri):
        self.db_uri = db_uri
        self.adc_uri = adc_uri
        self.ws_gui_db = None
        self.ws_gui_adc = None
        self.datastore = DS()
      

    async def connect_db(self):
        self.ws_gui_db = await websockets.connect(self.db_uri)
        print("Connected to DB server")

    async def connect_adc(self):
        self.ws_gui_adc = await websockets.connect(self.adc_uri)
        print("Connected to ADC server")

    async def handle_db(self):
        async for message in self.ws_gui_db:
            print("DB:", message)
            self.datastore.translate_message(message)
        
    async def handle_adc(self):
        async for message in self.ws_gui_adc:
            print("ADC:", message)

    async def run(self):
        # Connect both
        await asyncio.gather(
            self.connect_db(),
            self.connect_adc()
        )
        print(f"db_socket: {self.ws_gui_db}   adc_socket: {self.ws_gui_adc}")

        # Run both listeners concurrently
        await asyncio.gather(
            self.handle_db(),
            self.handle_adc()
        )
    async def send_db(self, msg):
        print("db cmd: ",msg)
        await self.ws_gui_db.send(msg)

    async def send_adc(self, msg):
        print("adc cmd: ",msg)
        await self.ws_gui_adc.send(msg)

async def main():
    client = GUIClient(
        db_uri="ws://localhost:8766",
        adc_uri="ws://localhost:8765"
    )

    # Start client in background
    task = asyncio.create_task(client.run())

    # Wait for connections to establish
    while client.ws_gui_db is None or client.ws_gui_adc is None:
        await asyncio.sleep(0.1)

    # Now safe to send
   # await client.send_db('300')       # save configuration
    await client.send_db('350')       # get configuration
    #await client.send_db('400')       # save measurement
    await client.send_db('450')       # get measurements
    #await client.send_db('500,0')    # save calibration
    await client.send_db('550,0')    # get calibrations
    #await client.send_db('600,0')    # save luts
    await client.send_db('650,0')    # get luts
    await client.send_adc('100,0')   #get measurement, chan 0
    await client.send_adc('100,1')   #get measurement, chan 0
    await client.send_adc('100,2')   #get measurement, chan 0
    await client.send_adc('200,0')   #get measurement, chan 0
    await client.send_adc('200,1')   #get measurement, chan 0
    await client.send_adc('200,2')   #get measurement, chan 0
    await client.send_adc('sd')        #show datastore: configs, measurments, calibrations, luts

    await task
    
asyncio.run(main())