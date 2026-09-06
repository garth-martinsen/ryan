#file: amps_row.py

from dataclasses import dataclass
#TODO: fit this into the flet  voltage_report panel 
@dataclass
class AmpsRow:
    CHAN: int
    TIMESTAMP: float
    I_MEAN: float
    PERIOD_SEC: int
    AH_USED: float
    AH_TOTAL: float

    def __str__(self):
        show= f"CHAN: {self.CHAN} TIMESTAMP: {self.TIMESTAMP} I_MEAN: {self.I_MEAN} PERIOD_SEC: {self.PERIOD_SEC: AH_USED: {self.AH_USED} AH_TOTAL: {self.AH_TOTAL}"
        return show
'''===========

# USAGE: in using module: from common.models.amps_row import AmpsRow
   {"CHAN":3, "TIMESTAMP": 178000.0, "I_MEAN":0.550,"PERIOD_SEC":3600, "AH_USED":0.550 }

=============='''
