import asyncio

async def handle_client(reader, writer):

    addr = writer.get_extra_info('peername')
    print("Connected:", addr)

    try:
        while True:
            data = await reader.read(100)

            if not data:
                break

            print("Received:", data)

            writer.write(b"ACK\n")
            await writer.drain()

    except Exception as e:
        print("Error:", e)

    finally:
        writer.close()
        await writer.wait_closed()
        print("Disconnected:", addr)

async def main():

    server = await asyncio.start_server(
        handle_client,
        '0.0.0.0',
        8888
    )

    print("Listening on port 8888")

    async with server:
        await server.serve_forever()

asyncio.run(main())
