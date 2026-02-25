#!/usr/bin/env python
# file: adc_ws_server.py

import asyncio
from websockets.asyncio.server import serve
from adc import ADC
from message_cfg import  msr_samples, clb_samples

adc=ADC()

async def echo(websocket):
    async for message in websocket:
        print("Client requested: ", message)
        response = adc.build_response(message)
        await websocket.send(response)

async def main():
    async with serve(echo, "localhost", 8765) as server:
        await server.serve_forever()

asyncio.run(main())
