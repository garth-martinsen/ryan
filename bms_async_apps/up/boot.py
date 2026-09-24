# boot.py -- run on boot-up
import network
from common.secrets import SSID, SSID_PASSWORD

# From common.secrets.py:
# print(f" From common.secrets.py:  SSID: {SSID}  SSID_PASSWORD: {SSID_PASSWORD}")

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(SSID, SSID_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('Connected! Network config:', sta_if.ifconfig())
    
print("Connecting to your wifi...")
do_connect()

