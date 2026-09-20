#fCell Vile: gui/components/bms_voltage_table_component.py 

import flet as ft
import flet_datatable2 as fdt
from common.models.voltage_row import VoltageRow
import time


def human_timestamp(tm: float):
    # return time.asctime(time.localtime(tm))
    return time.strftime( "%m/%d/%Y %H:%M:%S", time.localtime(tm))

def make_row(v: VoltageRow):
    return ft.DataRow(
        cells=[
            ft.DataCell(ft.Text(str(v.id_))),
            ft.DataCell(ft.Text(human_timestamp(v.timestamp))),
            ft.DataCell(ft.Text(v.type)),
            ft.DataCell(ft.Text(str(v.chan))),
            ft.DataCell(ft.Text(f"{v.vtap:.4f}")),
            ft.DataCell(ft.Text(f"{v.vcell:.4f}")),
        ]
    )


@ft.component
def BmsVoltageTable(rows):

    return fdt.DataTable2(
        expand=True,
        
        columns=[
            fdt.DataColumn2(label=ft.Text("Id"), fixed_width=55),
            fdt.DataColumn2(label=ft.Text("Timestamp")),
            fdt.DataColumn2(label=ft.Text("Type")),
            fdt.DataColumn2(label=ft.Text("Circuit")),
            fdt.DataColumn2(label=ft.Text("Cell V"), numeric=True),
            fdt.DataColumn2(label=ft.Text("Vtap V"), numeric=True),
        ],
        rows=[ make_row(r) for r in rows ],
    )
