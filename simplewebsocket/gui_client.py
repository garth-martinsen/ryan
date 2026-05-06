# file: gui_client.py
import asyncio
import websockets
from client_data_store import DataStore as DS
import time

db_uri = "db_ws_server:  localhost", 8766
class GUIClient:                                          
    def __init__(self, db_uri):  
        self.db_uri = db_uri
        self.ws_gui_db = None
        self.datastore = DS()
        self.millis=lambda: int(round(time.time() * 1000))

    def millisecs(self):
        return self.millis()
    
    def timestamp(self):
        """Returns local time as string, eg: YYYY-mm-DD HH:MM:SS"""
        dt = time.localtime()
        return f"{dt[0]}-{dt[1]}-{dt[2]}_{dt[3]}:{dt[4]}:{dt[5]}"  # YYYY-MM-DD  HH:mm:sec (dt[6] dow , dt[7] julian)
    
    async def connect_db(self):
        self.ws_gui_db = await websockets.connect(self.db_uri)
        print("Connected to DB server")

    async def handle_db(self):
        async for message in self.ws_gui_db:
            print("DB:", self.millisecs(),  message)
            self.datastore.translate_message(message)
        
    async def run(self):
        await asyncio.gather(
            self.connect_db()
        )
        print(f"db_socket: {self.ws_gui_db}")

        # Run db listener concurrently
        await asyncio.gather(
            self.handle_db()
        )
    async def send_db(self, msg):
        print("db cmd: ",msg, self.millisecs() )
        await self.ws_gui_db.send(msg)

async def main():
    client = GUIClient(
        db_uri="ws://localhost:8766"
    )

    # Start client in background
    task = asyncio.create_task(client.run())

    # Wait for connection to establish
#    while client.ws_gui_db is None or client.ws_gui_adc is None:
    while client.ws_gui_db is None:
        await asyncio.sleep(0.1)
        await client.send_db('310')       # get configurations for 3 circuits
        await client.send_db('312')       # get configurations for 3 circuits
        await client.send_db('314')       # get configurations for 3 circuits
        await client.send_db('360')       # get lut0
        await client.send_db('362')       # get lut1
        await client.send_db('364')       # get lut2
        await client.send_db('370')       # get lut0 timestamp
        await client.send_db('372')       # get lut1  timestamp
        await client.send_db('374')       # get lut2  timestamp
        await asyncio.sleep(5)
        await client.datastore.show_data_store()
        await task

asyncio.run(main())


''' codes for database interface to respond to:  from file: database_interface_config.py ...
100 request_measure
                   101 response_measurement
150 past_measurements_0
                  151 response: past_measurements_0
152 past_measurements_1
                153 response: past_measurements_1
154 past_measurements_2
                 155 response: past_measurements_2
200 request_calibrate
                  201 response_calibration
250 request_past_calibrations_0
                  251 response_past_calibrations_0
252 request_past_calibrations_1
                  253 response_past_calibrations_1
254 request_past_calibrations_2
                  255 response_past_calibrations_2
300 save_config
310 request_config
                  311 response_config
350 save_lut
360 request_lut_0
                 361 response_lut_0
362 request_lut_1
                  363 response_lut_1
364 request_lut_2
                  365 response_lut_2
370 request_lut0_timestamp
                  371 response_lut0_timestamp
372 request_lut1_timestamp
                  373 response_lut1_timestamp
374 request_lut2_timestamp
                  375 response_lut2_timestamp
'''
