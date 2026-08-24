# file gui/models/app_config.py

import flet as ft
from dataclasses import dataclass


@ft.observable
@dataclass
class AppConfig:
    id_: int
    owner : str
    app_desc: str
    timestamp: float
    tempC: float
    adc_fsr : float
    adc_steps: int
    adc_sample_rate: int
    version: int
    version_desc:str
