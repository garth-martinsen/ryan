# file: up/adc_asyncio_client.py 

from common.bms_config import SVR_IP, SVR_PORT 
import asyncio 
import json

print(f"From bms_config, SVR_IP: {SVR_IP}, SVR_PORT: {SVR_PORT}")

msg = {
    "SENDER": "ADC",
    "RECEIVER": "SVR",
    "CODE": 0,
}


async def tcp_client():
    """Connect to the server and send the initial registration message."""

    print("Opening connection to server...")

    reader, writer = await asyncio.open_connection(SVR_IP, SVR_PORT)

    packet = json.dumps(msg) + "\n"

    print("Sending:", repr(packet))
    writer.write(packet.encode())
    await writer.drain()
    print("Message sent; waiting for ACK...")

    data = await reader.readline()

    print("reader.readline() returned")
    print("Raw server response:", repr(data))

    if data:
        print("Decoded server response:", data.decode().rstrip())
    else:
        print("Server closed without returning data")

    print("Closing client connection")
    writer.close()
    await writer.wait_closed()
    print("Client connection closed")


"""
        print("Registration message sent:", packet.rstrip())

        # This waits until the server sends a newline-terminated response.
        data = await reader.readline()

        if not data:
            print("Server closed the connection without sending a response.")
        return

        #print("Message received from server:", data.decode().rstrip())
    finally:
        writer.close()
        await writer.wait_closed()

"""
if __name__ == "__main__":
    asyncio.run(tcp_client())
