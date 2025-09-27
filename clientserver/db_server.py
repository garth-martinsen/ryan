# file:  db_server.py from renamed server_0922.py
import socket
import threading
import json
from svr_data_controller_0922 import SvrDataController
HEADER = 64  # bit
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

DISCONNECT_MESSAGE = json.dumps(
    {"purpose": -1, "sender_id": "gui_client", "msg_id": -1,"desc": "DISCONNECT"}
)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

sdc = SvrDataController((1,2,3))


def handle_client(conn: socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        header = conn.recv(HEADER).decode(FORMAT)  # blocking line

        if not header:
            continue

        msg_len = int(header)
        amsg = conn.recv(msg_len).decode(FORMAT)
        msg=json.loads(amsg)
        print(f"[MESSAGE RECEIVED][{addr}] {msg}")
        if msg:
            response = sdc.handle_message(msg)
            print("response: ", response)
            if response:
                conn.send(response.encode(FORMAT))
            else:
                connected = False
 
    conn.close()


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()  # blocking line
        thread = threading.Thread(target=handle_client, args=(conn, addr))

        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] Server is starting ...")
start()
