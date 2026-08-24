#file: wifi_test.py
import network
import time

SSID = "Ziply1824"
PASSWORD = "1L0v3Samw1s3*#!"

w = network.WLAN(network.STA_IF)
w.active(True)

print("Connecting...")
w.connect(SSID, PASSWORD)

for i in range(30):
    status = w.status()
    print(f"{i:2d}: status={status}")

    if w.isconnected():
        print("\nConnected!")
        print("IP:", w.ifconfig())
        break

    time.sleep(1)
else:
    print("\nConnection failed.")
