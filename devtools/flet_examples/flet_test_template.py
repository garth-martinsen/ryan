# file: gui/tests/test_template.py

import flet as ft
from tested_class import model, view

def main(page: ft.Page):
    page.title="Testing XXXXX"
    page.render(AppView)


@ft.component
def AppView():
    config, set_config = ft.use_state(
        Chan_Config(
            id_=5,
            ...
        )
    )

ft.run(main)
''' This is only a temmplate... Do not run a test against this...'''
