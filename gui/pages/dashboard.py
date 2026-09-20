"""Index routes — default child routes with index=True."""

import flet as ft
from gui.components.bms_voltage_table_component import BmsVoltageTable
from common.models.voltage_row import VoltageRow
@ft.component
def Dashboard(voltage_rows):
#    print("Dashboard received:", voltage_rows)

    return ft.Column(controls=[
               ft.Row(controls = [ ft.Text("Dashboard: Battery Management System (BMS)", size=24)]),
               ft.Row( controls = [
                   BmsVoltageTable(voltage_rows),
            ])
        ])


@ft.component
def Configuration():
    return ft.Text("BMS Configuration /config", size=20)


@ft.component
def History():
    return ft.Text("Battery History /hist ", size=20)

@ft.component
def SecuritySettings():
    return ft.Text("Security Settings", size=20)


@ft.component
def SettingsLayout():
    outlet = ft.use_route_outlet()
    return ft.Column(
        [
            ft.Text("Settings", size=24),
            ft.Row(
                [
                    ft.Button(
                        "General",
                        on_click=lambda: ft.context.page.navigate("/settings"),
                    ),
                    ft.Button(
                        "Profile",
                        on_click=lambda: ft.context.page.navigate("/settings/profile"),
                    ),
                    ft.Button(
                        "Security",
                        on_click=lambda: ft.context.page.navigate("/settings/security"),
                    ),
                ]
            ),
            ft.Divider(),
            outlet,
        ]
    )


@ft.component
def App():

    voltage_rows, set_voltage_rows = ft.use_state([])
#            VoltageRow(176, 1783109112.0, "c", "1 Cell", 4.0323, 4.0323),
#            VoltageRow(177, 1783105513.0, "c", "2 Cells", 3.9760, 7.9990),
#            VoltageRow(178, 1783105514.0, "c", "3 Cells", 4.0774, 12.0674),
#])

    def update_voltage_rows(new_rows: list[VoltageRow]):
        set_voltage_rows(new_rows)

    @ft.component
    def DashboardRoute():
#       print("DashboardRoute rows:", voltage_rows)
       return Dashboard(voltage_rows=voltage_rows)

    return ft.SafeArea(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Button(
                            "Dashboard",
                            on_click=lambda: ft.context.page.navigate("/"),
                        ),
                        ft.Button(
                            "Configuration",
                            on_click=lambda: ft.context.page.navigate("/config"),
                        ),
                        ft.Button(
                            "History",
                            on_click=lambda: ft.context.page.navigate("/hist"),
                        ),
                        ft.Button(
                            "Commands",
                            on_click=lambda: ft.context.page.navigate("/commands"),
                        ),
                    ]
                ),
                ft.Divider(),
                ft.Router(
                    [
                        ft.Route(index=True, 
                        component=DashboardRoute),
                        ft.Route(
                            path="settings",
                            component=SettingsLayout,
                            children=[
                                ft.Route(index=True, component=DashboardRoute),
                                ft.Route(path="config", component=Configuration),
                                ft.Route(path="hist", component=History),
                                ft.Route(path="commands", component="Commands"),
                            ]
                        ),
                    ]
                ),
            ]
        )
    ) 


if __name__ == "__main__":
    ft.run(lambda page: page.render(App))

