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

class AdcClient:
    def __init__(self):
        print("Created AdcClient")
        self.tcp_client()

    async def tcp_client(self):
        """Connect to the server and exchange one test message."""

        print("Opening connection to server...")
        reader, writer = await asyncio.open_connection(SVR_IP, SVR_PORT)

        try:
            packet = json.dumps(msg) + "\n"

            print("Sending:", repr(packet))
            writer.write(packet.encode())
            await writer.drain()

            print("Message sent; waiting for ACK...")
            data = await reader.readline()

            print("reader.readline() returned:", repr(data))

            if data:
                print("Decoded server response:", data.decode().rstrip())
            else:
                print("Server closed without returning data")

        finally:
            print("Closing client connection")
            writer.close()
            await writer.wait_closed()
            print("Client connection closed")
def main():
    client = AdcClient()
    await client.tcp_client()

if __name__ == "__main__":
    asyncio.run(main())
