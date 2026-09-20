# gui/test_chan_config_component.py

import flet as ft

from gui.components.chan_config_component import (
    Chan_Config,
    Chan_Config_View,
)

def main(page: ft.Page):
    page.title= "Testing Channel Configuration Component"
    page.render(AppView)

# Test Harness, will execute if run  "python chat_edits_component.py" in terminal. Will be ignored if imported as a component. 

@ft.component
def AppView():
    config, set_config = ft.use_state(
        Chan_Config(
            id_=5,
            app_id =1,
            version = 3,
            version_desc = "PCB2",
            timestamp = 1782687301.567499,
            chan= 0,
            chan_desc = "One Cell 3.0-4.5V",
            capacitor = 1.0e-7,       # Need to measure and change accordingly
            R1 = 101100,
            R2 = 303700,
            vd_fract = 0.750247035573123,
            k_factor = 3.0,
            lut_version = 1,
            lut_calibrated= 0,
            lut_timestamp = 1782687301.5675,
        )
    )

    return [
    Chan_Config_View(config, set_config)
    ]

ft.run(main)

# ft.run(lambda page: page.render(AppView))



