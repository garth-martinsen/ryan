# file gui/models/chan_config.py

import flet as ft
from dataclasses import dataclass


@ft.observable
@dataclass
class Chan_Config:
    id_: int
    app_id: int
    version: int
    version_desc:str
    timestamp: float
    chan: int
    chan_desc: str
    capacitor: float
    R1: float
    R2: float
    vd_fract: float  
    k_factor: float
    lut_version: int
    lut_calibrated: int
    lut_timestamp: float

