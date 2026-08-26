# gui/test_bms_voltage_table-component.py
import flet as ft
from gui.components.bms_voltage_table_component import BmsVoltageTable
from common.models.voltage_row import VoltageRow


CIRCUIT_NAMES = ["1 Cell", "2 Cells", "3 Cells"]

voltage_rows = [
    VoltageRow(176, 1783109112.0, "c", CIRCUIT_NAMES[0], 4.0323, 4.0323),
    VoltageRow(177, 1783105513.0, "c", CIRCUIT_NAMES[1], 3.976, 7.999),
    VoltageRow(178, 1783105514.0, "c", CIRCUIT_NAMES[2], 4.0774, 12.0674),
]


@ft.component
def AppView():
    return [
        BmsVoltageTable(voltage_rows)
    ]


def main(page: ft.Page):
    page.title = "BMS Voltage Table Test"
    page.render(AppView)


ft.run(main)
