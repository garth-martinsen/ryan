# file: gui/pages/configuration.py

import flet as ft
from gui.components import chan_config_component

@ft.component
def Dashboard():
    return ft.Card(
        ft.Column(controls=[ 
            ft.Row(controls =[ 
                ft.Text("BMS Configuration: ", size=24) ]), 
                AppConfig(),
                ChanConfig(),
		ChanConfig(),
                ChanConfig(),
            ])) 

if __name__ == "__main__":
    ft.run(lambda page: page.render(App))

