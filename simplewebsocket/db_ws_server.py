#!/usr/bin/env python

import asyncio
from websockets.asyncio.server import serve
from   database_interface  import DatabaseInterface as DBI
from message_cfg import  msr_samples, clb_samples

dbi=DBI((1,2,3))

async def echo(websocket):
    async for message in websocket:
        print("Client requested: ", message)
        response = dbi.build_response(message)
#        response = ' TBD... work in progress'
        await websocket.send(response)

async def main():
    async with serve(echo, "localhost", 8766) as server:
        await server.serve_forever()

asyncio.run(main())
