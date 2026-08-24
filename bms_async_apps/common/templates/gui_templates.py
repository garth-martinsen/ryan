#file: gui/components/example_component_template.py

# EXAMPLE_ONLY  Replace X with your class

import flet as ft
from dataclasses import dataclass
import time


@ft.observable
@dataclass
class X:
    id_:int
    #...

def XView(newcomp: X, set_state):
    print("Rendering XView", id(newcomp))
    # helper methods needed...
    def blah():...
    return ft.Card(
        content=ft.Column(
            controls=[
               #...
             ]
        )
    )
def XForm(newcomp: X):
    return  ft.Column(
                controls=[
                  # ...
                ]
            )
# Test Harness will live in the test/test_newcomponent.py file...
