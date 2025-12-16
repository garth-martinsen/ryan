# file: adc.py  class to gather a2d samples for a circuit, process them and prepare report for server.


from adc_cfg import (
    names,
    i2c,
    Measurements,
    Stats,
    measurements,
    allPins,
    gatePins,
    ads,
    steps,
)
from collections import OrderedDict
from adc_cfg import adc_sample_rate, _BUFFERSIZE
from machine import Pin, SoftI2C, PWM, Timer
from time import ticks_us, ticks_diff, ticks_ms, localtime, time
import math
import sys
import time
import json
import asyncio

up = sys.implementation.name == "micropython"

datapath = "/Users/garth/DIST/clientserver/ryan/clientserver/data"


class ADC:
    def __init__(self):
        self.names = names
        # self.tolerance=tolerance
        self.channel = -99  # Must be one of [0,1,2] when running
        self.pins = allPins
        self.gates = gatePins
        self.measurements = measurements
        self.index_put = 0
        self.sample_period = 1 / _BUFFERSIZE
        self.gate_time = -1  # time (secs) from gate_open until gate_close on a circuit
        self.store_time = 0  # time needed to store a single pair of a2d & uclick values
        self._check_i2c()
        # self.wait_period = 60        # passed in in async method: schedule_tasks(); used to sleep before repeating.
        # self.tasks=[]                       # passed in in async method: schedule_tasks()
        self._initialize_gates()  # all gates set to high which stops all current flow
        self.first_sample = True
        self.lsb = 0  # set in the measurement method depending on channel
        self.luts: [OrderedDict, OrderedDict, OrderedDict] = [OrderedDict(), OrderedDict(), OrderedDict()]
        self.cfg_ids = ()
        self.configs = [[], [], []]
        self.vin = -99  # set in calibrate(...) else remains -99
        self.gain_per_chan = {0: 0, 1: 1, 2: 1}
        self.fs_per_chan = {0: 6.144, 1: 4.095, 2: 4.095}
        self.steps = steps

    def _check_i2c(self):
        """if ADS1115 ADDR pin is grounded, should return 72"""
        if i2c.scan()[0] == 72:
            print("i2c is working...")
        else:
            print("I2c is not working. Troubleshoot connections")

    def __str__(self):
        """Shows all of the self attributes..."""
        return f"adc attributes:  {self.__dict__.keys()}"

    def _timestamp(self):
        """Returns local time as string, eg: YYYY-mm-DD HH:MM:SS"""
        dt = time.localtime()
        return f"{dt[0]}-{dt[1]}-{dt[2]}  {dt[3]}:{dt[4]}:{dt[5]}"  # exclude day-of-week and julian date.

    def calibrate(self, chan, purpose, vin):
        # self.vin = float(input("Enter value of vin  "))
        self.vin = vin
        print(f"Called adc.calibrate(), Chan: {chan} Vin: {vin} purpose: { purpose}")
        return self.measure(chan, purpose)

    def measure(self, ch, purpose):
        """Prepares circuits[ch] to turn on current and sample voltages at the sample point.
        The sampled a2d values may be low if wait time is not enough."""
        # !!!always reset the counter, index_put,  before a measurement.!!!
        self.index_put = 0
        self.channel = ch
        ads.gain = self.gain_per_chan[ch]
        self.fs = self.fs_per_chan[ch]
        self.lsb = self.fs / 32768
        # print("gate open: " , gate_opened)
        self._turn_on(ch)
        gate_opened = ticks_us()
        # add handler for irq
        self.pins.alert.irq(trigger=Pin.IRQ_FALLING, handler=self._sample_auto)
        ads.conversion_start(adc_sample_rate, ch)
        # if channel==0 the a2d values will come from A0, if 1 then A1, if 2 then A2
        print("===========measuring=========")
        print(
            " Wait for samples...", _BUFFERSIZE, "  FS: ", self.fs, " LSB : ", self.lsb
        )
        # loops until a2d and uclicks arrays are filled
        while self.index_put < _BUFFERSIZE:
            pass
        print("Done...A2D samples will be found in self.measurements[self.channel].a2d")
        # start the current flowing...
        self._turn_off(self.channel)
        gate_closed = ticks_us()
        # print("gate closed: ", gate_closed)
        # time from gate_open until gate_close in µs converted to seconds
        self.gate_time = ticks_diff(gate_closed, gate_opened) / 1e6
        return self._process_and_report(ch, purpose)

    # IRQ method triggered by ADC ALRT pin when ADS is ready for sample to be read.
    def _sample_auto(self, x, samp=ads.alert_read):
        """Sets storage arrays depending on the active channel , measures storage time. The storage time must be less than 1/sample_rate."""
        a2d = self.measurements[self.channel].a2d
        uclicks = self.measurements[self.channel].uclicks
        # The 1st four samples which usually are too small are discarded...  see adx1115.py file ~line 88
        strt = ticks_us()  # can remove when realtime load is known.
        if self.index_put < _BUFFERSIZE:
            a2d[self.index_put] = samp()
            uclicks[self.index_put] = ticks_us()
            secs = ticks_diff(ticks_us(), strt) / 1e6
            # measured in µs, convert to secs.
            # stores the longest time needed to read, store a2d & uclicks comparing for each of  _BUFFERSIZE samples
            self.store_time = max(secs, self.store_time)
            self.index_put += 1

    def _turn_on(self, chn):
        """Setting the gate pin to LOW drains the P_Mosfet Gate Capacitor so Vgs goes negative.
        When Vgs < -2V, P_Mosfet conducts with full current."""
        self.gates[chn].off()
        self._show_gates()

    def _turn_off(self, chn):
        """Setting gate pin to HIGH allows pullup resistor to charge Mosfet Capacitor, turning off current."""
        self.gates[chn].on()
        self._show_gates()

    def _show_gates(self):
        print(self.gates[0], self.gates[1], self.gates[2])
        print((self.gates[0].value(), self.gates[1].value(), self.gates[2].value()))

    def _initialize_gates(self):
        """For a P-Channel Mosfet, when gate value is HIGH,  gate V  = Src V , so no current flows( ).
        Only 1 channel should be 0, ( conducting) at a time. Initializing sets all gateV=HIGH. no current in any circuit.
        """
        for i in range(3):
            self.gates[i].on()
        self._show_gates()

    def _process_and_report(self, chan, purpose):
        """Computes stats and rejects outliers, Looks up vb using vm
        Returns dict with stats & keep. The adc_client will send the payload to the server.
        payload returned depends on the purpose..."""
        print(f"in _process_and_report  purpose: {purpose} channel: {chan}")
        name = self.names[int(chan)]
        obj = None
        # TODO: DONE: find out why keep is not included in the obj which becomes the payload in _process_and_report(chan, purpose)
        keep, stats = self._stats(chan)
        # print("in process... keep: ", keep)
        vm = stats.vm_mean
        vin = self.vin
        print(" in _process_and_report()  chan: ", chan, "  vm: ", vm)
        vb = self._lookup_vb(chan, vm)
        error = vb - vin
        cfg_id = self.cfg_ids[chan]
        # report depends on the purpose: measure or calibrate
        if purpose == 100:
            # purpose 101 means report measurement to server.
            obj = {
                "purpose": 101,                       #will be popped from dict before save to db to yield a BMS record.
                "timestamp": self._timestamp(),
                "type": "m",
                "chan": chan,
                "cfg_id": cfg_id,
                "a2d": stats.a2d_mean,
                "a2d_sd": stats.sd,
                "sample_sz": len(keep),
                "vin": vin,  # ignored for meas
                "vm": vm,
                "vb": vb,
                "error": error,  # ignored for meas
                "sample_period": stats.sample_period,
                "store_time": stats.store_time,
                "gate_time": stats.gate_time,
                "keep": keep,               
            }
            print("obj: ", obj)
        elif purpose == 200:
            # 201 means report calibration to server
            obj = {
                "purpose": 201,                                 #will be popped from dict before save to db to yield a BMS record.
                "timestamp": self._timestamp(),
                "chan": chan,
                "cfg_id": cfg_id,
                "type": "c",
                "a2d": stats.a2d_mean,
                "a2d_sd": stats.sd,
                "sample_sz": len(keep),
                "vin": self.vin,
                "vm": vm,
                "vb": vb,
                "error": error,
                "sample_period": stats.sample_period,
                "store_time": stats.store_time,
                "gate_time": stats.gate_time,
                "keep": keep,
            }
            print(f" reporting back to server: {obj} ")
        return obj

    def _stats(self, channel):
        """performs _stats on all samples, uses sd, mean, and allowance to reject outliers, returns keep, __stats"""
        ch = int(channel)
        # get samples and do stats1 on them
        samples = self.measurements[ch].a2d
        m = sum(samples) / len(samples)
        m_vm = m * self.lsb
        var = [(x - m) ** 2 for x in samples]
        sd = math.sqrt(sum(var) / len(var))
        vin = self.vin
        # Stats = namedtuple("Stats", ("circuit_name",  "sample_sz", "mean", "sd", "sample_period","store_time","gate_time"))                                                                                           #7 fields

        theStats1 = Stats(
            self.names[ch],
            vin,
            len(samples),
            m,
            m_vm,
            sd,
            self.sample_period,
            self.store_time,
            self.gate_time,
        )
        print("theStats1: ", theStats1)
        # If  any  outliers  are discarded, return stats on keepers: a keeper falls within allowance of mean
        keep = [x for x in samples if abs(x - m) < theStats1.sd]
        if sd > 0 and len(keep) < len(samples):
            print("keep: ", keep)
            m2 = sum(keep) / len(keep)
            m_vm2 = m2 * self.lsb
            var2 = [(x - m2) ** 2 for x in keep]
            sd2 = math.sqrt(sum(var2) / len(var2))
            theStats2 = Stats(
                self.names[ch],
                vin,
                len(keep),
                m2,
                m_vm2,
                sd2,
                self.sample_period,
                self.store_time,
                self.gate_time,
            )
            print("theStats2: ", theStats2)
        return (keep, theStats2)

    def _bracket_vm(self, chan, vm):
        """using the lut from channel, bracket vm between two values: loval and hival. Works only for sorted(lut.items())
        returns tuple: (loval,vm, hival) for use in interpolation"""
        loval = hival = -99
        lut = self.luts[chan]
        for k, v in sorted(lut.items()):
            if k > vm:
                hival = k
                break
            elif k < vm:
                loval = k
        # print(f" low: {loval} vm: {vm} high: {hival}")
        return (loval, vm, hival)

    def _interpolate(self, chan, loval, vm, hival):
        """Assumes linearity between sample points, so interpolation should work"""
        #lut = json.loads(self.luts[chan])
        lut =self.luts[chan]
        rngx = hival - loval
        rngy = lut[hival] - lut[loval]
        pctx = (vm - loval) / rngx
        # print(f" rngx: {rngx}, mgy: {rngy}, fraction: {pctx}")
        bval = pctx * rngy + lut[loval]
        # print("vb: ", bval)
        return bval

    def _lookup_vb(self, chan, vm):
        """Returns the estimate of vb, channel voltage given measured voltage, vm"""
        # TODO: DONE: put a guard in to prevent asking for a lookup if vm is out of bounds. 7/26/25
        # TODO: Re-calibrate lut0
        # TODO 4 adc.li: 293: Fix lut so it is an OrderedDict and not a string.
        lut = self.luts[chan]
        print(f" lookup_vb()  type(lut) : { type(lut) }   lut: {lut}")
        print(f"called lookup_vb() chan: {chan}  vm: {vm}")
        lowest = min(lut)
        highest = max(lut)
        v = float(round(vm, 4))
        if v < lowest or v > highest:
            print(f" vm: {vm} does not lie between limits: ", lowest, " and: ", highest)
            print(
                "Vm is out of bounds for the Lookup Table...Check circuit with multimeter or re-calibrate LUT"
            )
            return -99
        else:
            (loval, v, hival) = self._bracket_vm(chan, vm)
            # print(f" low: {loval} , vm: {v} , high: {hival}")
            vb = self._interpolate(chan, loval, v, hival)
            print(f"Looking up vb given vm: {vm} on channel: {chan} gives: {vb}")
        # subtracting 0.0025355 causes error mean to go to zero on channel 0
        # TODO: investigate LUT0 values to see if db errors go away when updated.
        return vb
  
    '''
    async def schedule_measurements(self) :
        '''TBD'''
        print("called adc.schedule_measureents()")
    
    async def step_calibrate(self) :
        '''TBD'''
        print("called adc.step_calibrate(...)")
    '''
