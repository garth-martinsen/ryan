
@ft.component

async def receiver(reader, on_message):
     while True:
         line = await reader.readline()

         if not line:
             break

             data = json.loads(line.decode())
             on_message(data)

async def sender(writer):
    for template in gui_cmd_templates.values():
        msg = deepcopy(template)
        msg["TIMESTAMP"] = time.time()
        print("sending", msg)
        writer.write((json.dumps(msg) + "\n").encode())
        await writer.drain()
        await asyncio.sleep(1)

async def run_client(on_message):
    reader, writer = await asyncio.open_connection(HOST, PORT)

    # introduction, etc.

    await receiver(reader, on_message)

