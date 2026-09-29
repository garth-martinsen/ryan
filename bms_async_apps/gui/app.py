import flet as ft
from gui.services import GuiClient
from gui.services.tcp_client import run_client, receiver, sender
from collection import OrderedDict
from gui.pages.dashboard import Dashboard
from gui.pages.configuration import Configuration
from gui.pages.history import History

#TODO 1: create and start the TCP client to send/receive msgs to the Svr...

@ft.component
def App():

    # Application-wide state
    voltage_rows, set_voltage_rows = ft.use_state([])

    # Incoming-message handlers ...

    def handle_voltage(msg:dict):
        CIRCUIT_NAMES = ["1 Cell","2 Cells","3 Cells"]
        rows = [ VoltageRow(**row_dict) for row_dict in data["ROWS"] ]
        set_voltage_rows(rows)

    def  handle_time_sync(msg:dict):
	pass
    def  handle_app_config(msg:dict):
	pass
    def handle_chan_config(msg:dict):
	pass
    def  handle_bms_list(msg:dict):
	pass
    def handle_a2d_samples(msg:dict):
	pass
    def handle_lut(msg:dict):
	pass
    def handle_edit_lut_item(msg:dict):
	pass
    def  handle_edit_lut_timestamp(msg:dict):
	pass
    def handle_estimator_parms(msg:dict):
	pass


    handlers = OrderedDict({
        101: handle_voltage,
        201: handle_voltage,
        303: handle_time_sync,
        311: handle_app_config,
        313: handle_chan_config,
        331: handle_bms_list,
        341: handle_a2d_samples,
        351: handle_lut,
        353: handle_edit_lut_item,        
        361: handle_edit_lut_timestamp,
        391: handle_estimator_parms
    })

    @ft.component
    def DashboardRoute():
        return Dashboard(voltage_rows)

    return ft.SafeArea(
        content=ft.Column(
            controls=[
                # navigation
                ...,

                ft.Router(
                    [
                        ft.Route(
                            index=True,
                            component=DashboardRoute,
                        ),
                        ...
                    ]
                ),
            ]
        )
    )

    async def start_tcp():
        await run_client(handle_message)

if __name__ == "__main__":
    ft.run(lambda page: page.render(App))
