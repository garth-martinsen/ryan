#!/usr/bin/env python

from websockets.sync.client import connect
from client_data_store import DataStore
ds = DataStore()

def messages():
    with connect("ws://localhost:8765") as websocket:
        while True:
            msg = input("enter cmd to the ADC:" )
            websocket.send(msg)
            message = websocket.recv()
            print(f"Received: {message}")
            ds.translate_message(message)

messages()
