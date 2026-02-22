#file: main.py    testing deepsleep RTC memory and timing

from machine import deepsleep, Pin, RTC
from time import sleep
from array import array
import json
from collections import namedtuple
import random


DATA=namedtuple("DATA",( "reps", "mean", "sd", "time"))
FORMAT="utf8"
rtc=RTC()

def store(data):
    rtc.memory(b'0')
    strng= f"{data.reps}_{data.mean}_{data.sd}_{data.time}_"
    databytes= strng.encode(FORMAT)
    rtc.memory(databytes)
    
def retrieve():
    bts= rtc.memory()
    strng = bts.decode(FORMAT)
    ary = strng.split("_")
    return ary
    
def timestamp():
     dt = rtc.datetime()
     return f'{dt[0]}-{dt[1]}-{dt[2]}  {dt[4]}:{dt[5]}:{dt[6]}.{dt[7]}'

def main():
    ''' This functions does work, then transmits to db, saves reps, mean, sd to RTC Memory, then goes into a deepsleep to preserve power.
    When the timer expires, It retrieves values stored in RTC Memory, extracts the number of reps and increments it by 1 and
    repeats ad infinitum until User hits Control-C. Future work will exit main without a Control-C'''
    
    ary = retrieve()
    print("ary: ",ary)
    # extract reps from RTC Memory and increments it  by 1
    reps = int(ary[0])+1
    print()
    print(f"*****************Hey,I just awoke from a deepsleep . data retrieved from RTC Memory: {ary} **************")
    print()
    print(f"RTC time is: {timestamp()}")
    print("Will sleep normally for 3 seconds")
    sleep(3)
    print("3 seconds of normal sleep have passed.Measuring 4V,8V,12V channels, Sending results to db, Saving mean and sd to rtc.memory... ")
    # set the timer for deepsleep wakeup.
    ms= 3600000
#     ms = int(input("Input timer in milliseconds: " ))
    print(f"Going into deepsleep for {ms} milliseconds")
    # KLUGE: use random number generators to simulate the mean and sd from measurements...  Later work will call ADC to measure...
    mean=3.0 +random.randrange(1,45)/10
    sd=1.34e-3 + random.randrange(1,30)/10
    
    data=DATA(reps, mean, sd, timestamp() )
    #Saving data to RTC Memory
    store(data)
    wake =deepsleep(ms)   #milliseconds

main()
