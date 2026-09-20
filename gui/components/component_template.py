#file: gui/components/component_template.py


import flet as ft
from dataclasses import dataclass
import time


@ft.observable
@dataclass
class NewComponent:
    id_:int
    #...

def NewComponentView(newcomp: NewComponent, set_state):
    print("Rendering NewComponentView", id(newcomp))
    # helper methods needed...
    def blah():...
    return ft.Card(
        content=ft.Column(
            controls=[
               #...
             ]
        )
    )
def NewComponentForm(newcomp: NewComponent):
    return  ft.Column(
                controls=[
                  # ...
                ]
            )
# Test Harness will live in the test_newcomponent.py file...
