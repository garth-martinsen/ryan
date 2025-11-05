# file: gui_client.py    purpose: liason between gui and adc_client thru db_server. runs in python3 env.
# copied and modified from:  https://github.com/juliogema/python-basic-socket/blob/main/client.py
# Notes: For each server response, only one client request can be made eg: on purpose:11 can send request(20)
# TODO 2: Find out why the request to measure(0) from gui_client causes problems.


import socket
import json
from gui_data_controller import GuiDataController

"""All msgs must have fields: purpose, sender_id, msg_id.  The adc_client  Configuration includes [10,20,30,40,50]  50 tells server
that adc_client is READY for requests.
... Use the same and add request(60) for config records for gui_client. All msgs with purpose>99 require forwarding to the other
client. Following the response for 60, send following requests to test forwarding: 
100: measure(chan)
200: calibrate(chan, vin)
300: repeating measurement sequence includes [3 measure(chan), 1 wait].  Future...
400: repeating calibration sequence includes 3 sets of stepping vins with a delay to set Power supply. Future..."""
# =======client code=========
HEADER = 64    #bytes
PORT = 5050
FORMAT = "utf-8"
DISCONNECT_MESSAGE = json.dumps(
    {"purpose": -1, "sender_id": "gui_client", "desc": "DISCONNECT"}
)
SERVER = "192.168.254.19"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

gdc=GuiDataController((1,2,3), client)

def send(msg):
    #global svr_msgs_cnt, resps_from_svr, rqsts_to_svr
    # msg is a string. First encode it into bytes, then get  and format length into 64 bytes.
    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_length = str(msg_len).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    # send length of message and then send message.
    client.send(send_length)
    client.send(message)
    # receive msg from server========blocking method =============
    while True:
        amsg = client.recv(2024)
        gdc.svr_msgs_cnt += 1
        #print(f"amsg in client.recv(): {amsg} ")
        if amsg:
            msg = json.loads(amsg)
            print(f" in gui_client.send.client.recv()  type: {type(msg)} msg: {msg} ")
            next_msg = gdc.handle_message(msg )
            print(f"next_msg: {next_msg}")
            if next_msg:
                send( next_msg)
            else:
                pass


# called methods-----
send(gdc.hi())
#send(gdc.bye())
# chan=0
# send(gdc.schedule_measure(chan))
# send(gdc.rqst_calibration(chan, 3.6))
     




