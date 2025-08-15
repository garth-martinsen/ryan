# file: data_controller.py path: /Users/garth/DIST/clientServer/ryan/clientserver/data_controller.py

"""This class will provide data services for all guis. It can also start asyncio tasks:
Calibrate(...), Measure(...) and  Wait(...)
It will Store and retrieve json files from/to DB and will convert  LUTS to python dicts(float,float)
The database interface,dbi, will be instantiated only when path to sqlite3 db file is provided. Config
can be requested from dbi only after the row ids of the application channels are passed from webserver.
"""

# import math
# import asyncio
# import os
# import rpvdclass
import time
import ast
import random
import json
from data_controller_config import Lut_Limits, lsb, circuits
from database_interface import DatabaseInterface, BMS
from collections import OrderedDict


class DataController:
    """Provides access to database and flet view (TBD). Constructor requires a
    tuple with the 3 ids that represent the configuration"""

    def __init__(self, cfg_ids):
        self.cfg_ids = cfg_ids
        self.cfg = []  # cfg will hold 3 channels of dict [0,1,2]
        self.luts = [
            {},
            {},
            {},
        ]  # lut will hold 3 Dictionaries: lut42, lut84 and lut126
        self.lut_limits = {}  # dict {channel: lut_limits} channels are: 0,1,2
        self.dbi = DatabaseInterface()
        self.lsb = 4.095 / pow(2, 15)  # ~ 125 µvolts
        self.limit = 255e-6
        self.row_id = 0
        self.load_config(self.cfg_ids)

    def cfg_ids(self):
        return self.cfg_ids

    def list_all_choices(self):
        return self.dbi.list_all_choices()

    def load_config(self, ids):
        """Loads db records with ids. Converts Luts to {float:float } and sets limits to iteration.
        This method loads Calibrate View."""
        self.cfg_ids = ids
        self.cfg = self.dbi.load_config(ids)
        for i in range(3):
            self.convert_lut(self.luts[i], i)

    def _limit_lut(self, channel):
        """checks if lut has data, if so it sorts the keys and selects alut[0] for lower and alut[-1]  for upper."""
        alut = OrderedDict(sorted(self.luts[channel].items()))
        #print("alut: ", alut)
        if len(alut) > 1:
            ord_keys = list(alut.keys())
            vm_low = ord_keys[0]
            vb_low = alut[vm_low]
            vm_high = ord_keys[-1]
            vb_high = alut[vm_high]
            # print("Lower Limit: ", lower_limit)
            # print("Upper Limit: ", upper_limit)
            length = (
                len(alut) - 1
            )  # stopping value for row_id, prevents out of bounds on list error
            self.lut_limits[channel] = Lut_Limits(
                circuits[channel], vm_low, vb_low, vm_high, vb_high, length
            )
            print(f"voltage limits to lut {circuits[channel]} are set.")

    def show_lut_limits(self, channel):
        return self.lut_limits[channel]

    def show_luts_and_limits(self):
        for i in range(3):
            print(f"=========channel {i}======================")
            print(f"LUT({i}): ", self.luts[i])
            print()
            print(f"LUT_LIMITS ({i}): ", self.lut_limits[i])
            print()

    def convert_lut(self, lut, channel):
        """LUT from the db fetch is a dict {str:float}, change keys so: dict{float:float }
        and store in memory for lookup use."""
        lut = self.luts[channel]
        lutdict = ast.literal_eval(self.cfg[channel].LUT)
        # lutdict = json.load(self.cfg[channel].LUT)
        # make lutdict a dict{float:float} and store it in proper place
        for k, v in lutdict.items():
            lut[float(k)] = v
        self._limit_lut(channel)

    # For in-memory lut.
    def sort_lut(self, channel):
        """Returns None. Sorts the lookup table by the keys in memory"""
        lut = self.luts[channel]
        alut = OrderedDict(sorted(lut.items()))
        self.luts[channel] = alut

    def save_measurement(self, msg):
        """Purpose: save measurement on a channel to the db.
        The db_interface will use msg values for the insert statement."""
        #print("datacontroller.save_measurement() called with args: cols, vals")
        self.dbi.save_measurement(msg)

    def save_calibration(self, msg):
        """Purpose: call databaseInterface to save info in table: BMS"""
        self.dbi.save_calibration(msg)

    # in-memory update
    def update_lut(self, channel, vb, new_vm):
        """Calibrate Gui has requested an update to the in-memory lut on a channel .
        Every time a lut gets a new dict pair, it is added at the end of the dict, so the
        new lut must be resorted, and supplied with limits. Design approach is to find item in
        lut by vb. if found:  remove the item.  Then add the incoming {vm:vb} to lut
        dict. Create a new lut from sorted lut. Replace the in-memory luts [channel] with the
        newly created one."""
        msg = f"Update  lut on channel : {channel} for item: {vb} : {new_vm}."
        print(f"TBD: DataController will {msg}")
        alut = self.luts[channel]
        # if old item is in dict, remove it  by finding vb
        theKey = None
        for k, v in alut.items():
            if v == vb:
                theKey = k
                break
        # if vb not in dict values then theKey =None which fails in following if
        if theKey:
            print("Removing theKey/value for : ", theKey)
            alut.pop(theKey, None)  # done: the pair is removed.
        # add the correct key and value . This replaces the old item but at end of dict
        alut[new_vm] = vb
        # sort newlut to go from least to greatest vb, by creating a newlut, then store it where old lut was.
        newlut = OrderedDict(sorted(alut.items()))
        self.luts[channel] = newlut
        self._limit_lut(channel)

    def measure(self, circuit):
        """Initiates asyncio task to sample, process and return vm, sd"""
        print(
            f"TBD: DataController  will initiate asyncio task to measure vm in circuit {circuit}  "
        )
        print(
            "I will wait to receive a list of a2d  values , compute their mean & sd, reject outliers, "
        )
        print("return vm=_as_volts(mean(a2d),  a2d_sd)")

    def list_lut_files(self):
        """Presents to user the list of lut files for circuit circ"""
        # print(f"TBD: Presents to user the list of lut files for each circuit")
        print("==================")
        for lt in self.luts:
            print(lt)
            print("==================")

    def estimate_vb(self, vm, channel):
        """Given measured voltage, vm, and appropriate LUT, Estimate the battery voltage, vb."""
        alut = self.luts[channel]
        ord_keys = sorted(alut.keys())
        limits = self.lut_limits[channel]
        if limits.lower_limit > vm or limits.upper_limit < vm:
            print("outside of limits. try again...")
            return
        else:
            l = u = -99  # init with silly
            for k in ord_keys:
                if k > v:
                    u = k
                    break
                else:
                    l = k
            return round(alut[l] + (v - l) / (u - l) * (alut[u] - alut[l]), 7)

    def _as_volts(self, a2d_mean, a2d_sd, channel):
        """Maps a2d  to voltage. Returns None"""
        vm = a2d_mean * self.lsb
        vm_sd = a2d_sd * self.lsb
        return (vm, vm_sd)

    def _do_stats(self, a2d, channel):
        """computes mean and sd for the a2d list passed in."""
        mean = sum(a2d) / len(a2d)
        var = []
        for s in a2d:
            var.append((mean - s) ** 2)
        sd = sum(var) / len(var)
        return (mean, sd, channel)

    def _reject_outliers(self, channel, a2d, mean, sd, tol):
        """Reject samples that are outside of tol*sd. and return (mean, sd) of keepers."""
        keep = [x for x in a2d if (x - mean < abs(tol * sd))]
        # get mean, sd of the keepers
        (m2, sd2, channel) = self._do_stats(keep, channel)
        return (m2, sd2, channel)

    def reverse_lookup(self, vin, channel):
        # print("vin: ", vin)
        for k, v in self.luts[channel].items():
            # print("key: ", k, "value: ", v)
            if v == vin:
                break
                # print("returning key: ", k)
        return k
    
    def update_gui(self, jsonx):
        '''The adc client has reported on a measurement or a calibration. Actions TBD'''
        print( f" GUI will receive jsonx: {jsonx}")
        