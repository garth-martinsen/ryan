#file: bms_config.py
'''This will be imported by svr, adc_client and gui_client so they can communicate.'''
import os

print("os is : ", os.getcwd())

SSID = "Ziply1824"
SSID_PASSWORD = "XXXXXXXXXXXXXX"

SVR_IP =  '192.168.88.2' 
SVR_PORT =8888

APP_ID = 1
VERSION = 3

VINS= [4.094, 7.97, 12.01]
