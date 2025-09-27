# file: adc_client.py
# ref: https://github.com/juliogema/python-basic-socket/blob/main/client.py
# ref: https://duckduckgo.com/?q=tech+with+tim+socket+programming&atb=v314-1&ia=videos&iax=videos&iai=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QiPPX-KeSc
import socket
import json
from adc_data_controller import AdcDataController


# instantiate the adc_data_controller. it will populate cfg_ids and luts later from db_server requests.
dc = AdcDataController()
purpose = -2
DISCONNECT_MESSAGE = json.dumps(
    {"purpose": -1, "sender_id": "adc_client", "desc": "DISCONNECT"}
)
HEADER = 64
PORT = 5050
FORMAT = "utf-8"
SERVER = "192.168.254.19"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def send(msg):
    """msg is a string, encodes into bytes, sends len and message"""

    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_length = str(msg_len).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    # receive msg from server========blocking=============
    while True:
        amsg = client.recv(2048).decode(FORMAT)
        # print(f"amsg received from svr : { type(amsg)}  {amsg}")
        if not amsg:
            continue
        msg = json.loads(amsg)
        # print(f" rmsg: {type(rmsg)} {rmsg}")  # rmsg is hopefuly a dict
        response = dc.handle_message(msg)
        send(response)


send(dc.greet_and_register())
# send(dc.disconnect())
