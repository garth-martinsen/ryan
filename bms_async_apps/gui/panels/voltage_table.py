import flet as ft
import flet_datatable2 as fdt

class VoltageTable(ft.Column):
    def __init__(self):
        super().__init__()
        table=fdt.DataTable2(
                expand=True,
                min_width=600,
                columns=[
                    fdt.DataColumn2(label="Timestamp", fixed_width=250),
                    fdt.DataColumn2(label="Circuit", fixed_width=150),
                    fdt.DataColumn2(label="Series(volts)", fixed_width=160, numeric=True),
                    fdt.DataColumn2(label="Cell(volts)", fixed_width=150, numeric=True),
                ],
                rows=[
                    ft.DataRow( 
                        cells=[
                            ft.DataCell(ft.Text("Tue Jul 21 07:24:38 PDT 2026")),
                            ft.DataCell(ft.Text("cell 1 :")),
                            ft.DataCell(ft.Text("3.65")),
                            ft.DataCell(ft.Text("3.65")),
                        ],
                    ),
                    ft.DataRow( 
                        cells=[
                            ft.DataCell(ft.Text("Tue Jul 21 07:24:39 PDT 2026")),
                            ft.DataCell(ft.Text("cells 1-2 : ")),
                            ft.DataCell(ft.Text("7.55")),
                            ft.DataCell(ft.Text("3.9")),
                        ],
                    ),
                    ft.DataRow( 
                        cells=[
                            ft.DataCell(ft.Text("Tue Jul 21 07:24:40 PDT 2026")),
                            ft.DataCell(ft.Text("cells 1-3 :")),
                            ft.DataCell(ft.Text("11.35")),
                            ft.DataCell(ft.Text("3.8")),
                        ],
                    ),
                ],
            )

        self.controls.append(table)


