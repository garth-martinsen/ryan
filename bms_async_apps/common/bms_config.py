#file: bms_config.py
'''This will be imported by svr, adc_client and gui_client so they can communicate.'''
import os

print("bms_config os.getcwd() is : ", os.getcwd())

SVR_IP =  '192.168.88.3' 
SVR_PORT =8888

APP_ID = 1
VERSION = 3

VINS= [4.094, 7.97, 12.01]

