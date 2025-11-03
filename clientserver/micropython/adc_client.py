# file: adc_client.py
# ref: https://github.com/juliogema/python-basic-socket/blob/main/client.py
# ref: https://duckduckgo.com/?q=tech+with+tim+socket+programming&atb=v314-1&ia=videos&iax=videos&iai=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QiPPX-KeSc
import socket
import json
from adc_data_controller import AdcDataController

# instantiate the adc_data_controller. it will populate cfg_ids and luts later from db_server requests.
purpose = -2
DISCONNECT_MESSAGE = json.dumps(
    {"purpose": -1, "sender_id": "adc_client", "desc": "DISCONNECT"}
)
HEADER = 64
PORT = 5050
FORMAT = "utf-8"
SERVER = "192.168.254.19"
ADDR = (SERVER, PORT)
dc = AdcDataController((1,2,3))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def send(msg):
    """msg is a string, This will encode into bytes, then send len and send message"""
    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_length = str(msg_len).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    print(f"send_length: {send_length} ")
    client.send(send_length)
    print(f"in adc_client.send(...) line 31 type(message): {type(message)}  message: {message} ")
    if msg:
        client.send(message)

    while True:
        # receive msg from server========blocking=============
        amsg = client.recv(2048).decode(FORMAT)
        print(f"before json.loads(amsg): {amsg} ")
        msg = json.loads(amsg)
        #print(f"amsg received from svr : { type(amsg)}  {amsg}")
        if  msg:
            print(f"adc.send() received type(msg): {type(msg)} msg:{msg}")  # msg is hopefuly a dict
            obj = dc.handle_message(msg)
            if obj:
                response =  json.dumps(obj)
                print(f"in send(...)  msg: {type(response)} {response}")
                send(response)
            else:
                continue


send(dc.greet_and_register())
# send(adc.configure())             
# send(adc.disconnect())






