#file: voltage_row.py

import flet as ft
from dataclasses import dataclass

@dataclass
class VoltageRow:
    id_: int
    timestamp: float
    type: str
    chan: int
    vcell: float
    vseries: float

