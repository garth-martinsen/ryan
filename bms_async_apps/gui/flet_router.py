# file: bms_router.py
#file: router.py  copied from https://flet.dev/docs/controls/router#routing
'''
The Router subscribes to on_route_change and re-renders automatically when the route changes.
Navigation is done via push_route or navigate.
When manage_views is True, the Router returns a list of View objects (one per path level) instead of a single component tree. This enables swipe-back gestures, system back button, and AppBar implicit back button on mobile. Must be used with render_views.
Parameters:
routes (list[Route]) - List of top-level Route definitions.
not_found (Callable | None, default: None) - Optional component to render when no route matches (404).
manage_views (bool, default: False) - When True, produce a list of View objects (one per path level) instead of a single component tree. Route components should return View instances with route and appbar set. Use with render_views.
'''
"""Basic Router — simplest example with flat routes."""

import flet as ft
import flet_msg_creator
from collections import OrderedDict
import  gui_asyncio_client as gui_client
from bms_classes import  BMS_Config, BMS_Record, BMS_LUT, BMS_App
import bms_config_component

@ft.component
def Home():
    return ft.Text("BMS Home", size=24)

@ft.component
def About():
    return ft.Text("About BMS", size=24)

@ft.component
def Config():
    return ft.Text("BMS Configuration", size=24)

@ft.component
def Server():
    svr_cmds =  OrderedDict({300: 'save_config(  msg : Config )', 302 : 'sync_time()',
                        310: 'get_config( chan : int )', 320: 'save_to_bms( msg :BMS )',
                        330: 'list_bms( chan:int, atype:str) ', 340: 'get_bms_a2d_samples( bms_id : int)',
                        350: 'get_lut( chan:int)', 352: 'get_lut_item(chan:int, vin:float)',
                        360: 'get_lut_timestamp( chan:int )', 370: 'update_lut_pair(  _id:int,   vm:float,   vin:float)',
                        380: 'update_lut_timestamp( chan:int )', 390: 'get_vd_fracts( )'})

    #print("cmds : ", svr_cmds)
    return ft.Column( controls = [
        ft.Text("Server Commands", size=20, weight=ft.FontWeight.BOLD),
        ft.Text(svr_cmds),
        flet_msg_creator.Message_Creator(),
        #bgcolor=ft.Colors.SURFACE_BRIGHT,
        #padding=10, 
        #ft.Container(content=outlet, padding=20),
        ft.Text("Footer - (c) 2026", text_align=ft.TextAlign.CENTER),
        ],
    )

@ft.component
def ADC():
    
        adc_cmds =  OrderedDict({100: 'measure( )',
                                                     174 : 'start_periodic_measurements(period, reps)',
                                                     200: 'calibrate( vin0, vin1, vin2)',
                                                     274: 'start_periodic_calibrations( period, reps, vin0,vin1, vin2 )'})
        return ft.Column( controls = [
        ft.Text("ADC Commands", size=20, weight=ft.FontWeight.BOLD),
        ft.Text(adc_cmds, width = 300),
        flet_msg_creator.Message_Creator(),
        #bgcolor=ft.Colors.SURFACE_BRIGHT,
        #padding=10, 
        #ft.Container(content=outlet, padding=20),
        ft.Text("Footer - (c) 2026", text_align=ft.TextAlign.CENTER),
        ],
    )               
    #return ft.Text("ADC Commands", size=24)


@ft.component
def App():
    return ft.SafeArea(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Button( "BMS Home", on_click=lambda: ft.context.page.navigate("/"),),
                        ft.Button( "About", on_click=lambda: ft.context.page.navigate("/about"),),
                        ft.Button( "Config", on_click=lambda: ft.context.page.navigate("/config"),),
                        ft.Button( "Server Commands", on_click=lambda: ft.context.page.navigate("/server"),),
                        ft.Button( "ADC Commands", on_click=lambda: ft.context.page.navigate("/adc"),),
                    ]
                ),
                ft.Router(
                    [
                        ft.Route(index=True, component=Home),
                        ft.Route(path="about", component=About),
                        ft.Route(path="config", component=Config),
                        ft.Route(path="server", component=Server),
                        ft.Route(path="adc", component=ADC),
                    ]
                ),
            ]
        )
    )


if __name__ == "__main__":
    ft.run(lambda page: page.render(App))
