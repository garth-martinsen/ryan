# file: data_controller.py

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
from database_interface import DatabaseInterface, BMS, CALIBRATE

# print("owner: ", owner, "app_id: ", app_id, "version_id:", version_id)


class DataController:
    ''' Provides access to database and flet view (TBD). Constructor requires a
    tuple with the 3 ids that represent the configuration'''

    def __init__(self, cfg_ids):
        self.cfg_ids =cfg_ids
        self.cfg = []  # cfg will hold 3 channels of dict [0,1,2]
        self.luts = [ {}, {},{} ]  # lut will hold 3 Dictionaries: lut42, lut84 and lut126
        self.lut_limits = {}  # dict {channel: lut_limits} channels are: 0,1,2
        self.dbi = DatabaseInterface()
        self.lsb = 4.095 / 2e15  # ~ 125 µvolts
        self.limit=255e-6
        self.row_id=0
        self.load_config(self.cfg_ids)
     
    def cfg_ids(self):
        return self.cfg_ids
    
    def list_all_choices(self):
        return self.dbi.list_all_choices()
        
    def load_config(self, ids):
        '''Loads db records with ids. Converts Luts to {float:float } and sets limits to iteration.
          This method loads Calibrate View.'''
        self.cfg_ids = ids
        self.cfg= self.dbi.load_config(ids)
        for i in range(3):
            self.convert_lut(self.luts[i],i)  
        
    def readable_timestamp(self, ts):
        """Returns a string with a human readable datetimestamp,
        when time.time() seconds are passed in"""
        t = time.localtime(ts)
        astr = f" {t.tm_year}/{t.tm_mon}/{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}"
        return astr

    def _limit_lut(self, channel):
        """checks if lut has data, if so it sorts the keys and selects alut[0] for lower and alut[-1]  for upper."""
        alut = dict(sorted(self.luts[channel].items()))
        print("alut: ", alut)
        if len(alut) > 1:
            ord_keys =list(alut.keys())
            vm_low= ord_keys[0]
            vb_low=alut[vm_low]
            vm_high = ord_keys[-1]
            vb_high = alut[vm_high]
            # print("Lower Limit: ", lower_limit)
            # print("Upper Limit: ", upper_limit)
            length = (len(alut) - 1)  # stopping value for row_id, prevents out of bounds on list error
            self.lut_limits[channel] = Lut_Limits(circuits[channel], vm_low, vb_low, vm_high, vb_high, length)
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
        #lutdict = json.load(self.cfg[channel].LUT)
        # make lutdict a dict{float:float} and store it in proper place
        for k, v in lutdict.items():
            lut[float(k)] = v
        self._limit_lut(channel)

    # For in-memory lut.
    def sort_lut(self, channel):
        """Returns None. Sorts the lookup table by the keys in memory"""
        lut = self.luts[channel]
        alut = dict(sorted(lut.items()))
        self.luts[channel] = alut

    # helper method to build the insert tuples: Columns, values
    def get_lists_for_insert(self, channel):
        """Returns db_column and values for insert statement. channel is passed in,
        it is used to get the values of each valuefield in self.cfg[channel]"""
        # TODO: See if this can be modified on the fly for different columns.
        # TODO: Note: creation time should be now, version should be incremented, version_desc should be created by user.

        valuefields = [
            "channel",
            "version",
            "version_desc",
            "channel_desc",
            "creation_time",
            "tempC",
            "mosfet",
            "mosfet_type",
            "r1",
            "r2",
            "rp",
            "rg",
            "LUT",
        ]
        db_columns = "(ID, CHANNEL_ID, VERSION_ID, VERSION_DESC, CHANNEL_DESC, TIMESTAMP, TEMPC, MOSFET_ID, MOSFET_TYPE, R1, R2, RP, RG, LUT)"
        values = []
        for vf in valuefields:
            val = self.cfg[channel].__getattribute__(vf)
            values.append(val)
        return db_columns, values

    def save_measurement(self, msg):
        ''' Purpose: save measurement on a channel to the db.
           The db_interface will use msg values for the insert statement.'''
        print("datacontroller.save_measurement() called with args: cols, vals")
        self.dbi.save_measurement(msg)
      
    def save_calibration(self, msg):
        '''Purpose: call databaseInterface to save info in table: BMS '''
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
        newlut = dict(sorted(alut.items()))
        self.luts[channel] = newlut
        self._limit_lut(channel)

    # TODO 2: Continue to implement with dbi. Too much db in this class.

    # inserts new record in table CONFIG with updated lut for channel_id and versions_id, prompt for version_desc
    #     def store_lut( self, channel):
    #         '''Stores a new record into CONFIG table with new LUT in two steps:
    #         1. insert a record with same values for each field except fields:
    #         channel, version_id, version_description, timestamp, and the modified column
    #         2. update that record with the new value for LUT
    #         '''
    #         print("DataController says: I will store a valid json string of in-memory lut to db config table")
    #         print(" with new version and version description")
    #         new_version =  self.cfg[channel].version + 1
    #         version_desc = input('Enter a reason for this new version:')
    #         #jsonize the LUT
    #         lut_json= json.dumps(self.luts[channel])
    #         self.dbi.store_lut(lut_json, channel, new_version, version_desc)

    def calibrate(self, vin, channel, reps, tolerance):
        '''Requests best vm when battery is at vb voltage. Used to build dependable LUT for circuit;
        vin is battery voltage driving the voltage divider, channel is one of: [C42, C84, C126] eg: [0,1,2]
        reps is number of samples. tolerance is # of sd allowed  from the mean, used to reject outliers.
        Returns a mock 7-tuple, "randomized row",  given the input voltage.
        This function will be replaced
        In the real world  where 4 of the 7-tuple come from
        DataController.calibrate(vin) function and where calibrate can be one of [True,False]   '''
     
     #KLUGE--KLUGE--KLUGE--KLUGE--KLUGE--KLUGE--KLUGE--KLUGE
        self.row_id += 1
        vm0 = self.reverse_lookup(vin, channel) 
        vm= vm0 + float(random.randint(-5,5)/10 *122e-6)
        sd= random.randint(-5,5)*122e-6
        vb= vin/vm0 * vm
        err= vb-vin
        if abs(err) < self.limit :   #see line 33
            calibrated = True
        else:
            calibrated = False
        row_tuple = (self.row_id, vin, vm, sd, vb, err, calibrated)
        #print("row_tuple: ", row_tuple)
        return row_tuple
    
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
        '''Presents to user the list of lut files for circuit circ'''
        # print(f"TBD: Presents to user the list of lut files for each circuit")
        print("==================")
        for lt in self.luts:
            print(lt)
            print("==================")

    def estimate_vb(self, vm, channel):
        '''Given measured voltage, vm, and appropriate LUT, Estimate the battery voltage, vb.'''
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
        '''Maps a2d  to voltage. Returns None'''
        vm = a2d_mean * self.lsb
        vm_sd = a2d_sd * self.lsb
        return (vm, vm_sd)

    def _do_stats(self, a2d, channel):
        '''computes mean and sd for the a2d list passed in.'''
        mean = sum(a2d) / len(a2d)
        var = []
        for s in a2d:
            var.append((mean - s) ** 2)
        sd = sum(var) / len(var)
        return (mean, sd, channel)

    def _reject_outliers(self, channel, a2d, mean, sd, tol):
        '''Reject samples that are outside of tol*sd. and return (mean, sd) of keepers.'''
        keep = [x for x in a2d if (x - mean < abs(tol * sd))]
        # get mean, sd of the keepers
        (m2, sd2, channel) = self._do_stats(keep, channel)
        return (m2, sd2, channel)

    def reverse_lookup(self, vin, channel):
        #print("vin: ", vin)
        for k,v in self.luts[channel].items():
            #print("key: ", k, "value: ", v)
            if v == vin:
                break
                #print("returning key: ", k)
        return k

            
        