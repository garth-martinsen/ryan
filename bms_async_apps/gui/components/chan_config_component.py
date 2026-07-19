#file: learn_flet/chan_config_component.py

import flet as ft
from dataclasses import dataclass
import time
from copy import deepcopy

# an x_component.py will contain: dataclass, view, form, test_harness (AppView)

@ft.observable
@dataclass

class Chan_Config:
    id_: int
    app_id: int
    version: int
    version_desc:str
    timestamp: float
    chan: int
    chan_desc: str
    capacitor: float
    R1: float
    R2: float
    vd_fract: float  
    k_factor: float
    lut_version: int
    lut_calibrated: int
    lut_timestamp: float

def human_timestamp( tm:float):
    return time.asctime(time.localtime(tm))                    

@ft.component
def Chan_Config_View(config: Chan_Config, set_config):
    print("Rendering Chan_Config_View", id(config), config.capacitor)
    edits = deepcopy(config)
    def close_dialog(e):
        print("called close_dialog()")
        # Close the dialog 
        ft.context.page.pop_dialog()
        
    def edit_channel(e):
        print(f"entered handler for edit_channel with {e}")
        print(f"config: {config}")
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Channel Configuration"),
            content=ConfigChanForm(edits),
            actions=[ ft.Button("Save", on_click=save_channel ), ft.Button("Cancel", on_click=close_dialog ) ] )

        ft.context.page.show_dialog(dlg)
        
    def save_channel(e):
        print("save_channel was called.")   
        print(f"edits : {edits}, config: {config}")
        print(f"edits.__dict__ : {edits.__dict__}")
        # update config from edits
        print("config id:", id(config))
        set_config(edits)
        print(f"after updating config from edits:  {config}")
        close_dialog(e)
           
    def cancel_channel(e):
        print("cancel_common was called.")
        close_dialog(e)
  
    return ft.Card(
        content=ft.Column(
            controls=[
                ft.Row(controls=[
                ft.Text(f"id_: {config.id_}",   width=200), ft.Text(f"app_id: {edits.app_id}",  width=200),]),
                 ft.Row(controls=[
                ft.Text(f"version: {edits.version}", width=200), ft.Text(f"version_description: {edits.version_desc}", width=200)]),               
                ft.Row(controls=[
                ft.Text(f"Channel: {edits.chan}", width=200), ft.Text(f"Channel_description: {edits.chan_desc}", width=200)]),
                ft.Row(controls=[
                ft.Text(f"timestamp: {human_timestamp(edits.timestamp)}", width=200), ft.Text(f"Capacitor: {edits.capacitor}", width=200)]) ,
                ft.Row(controls=[
                ft.Text(f"R1: {edits.R1}", width=200) , ft.Text(f"R2: {edits.R2}", width=200)]) ,
                ft.Row(controls=[
                ft.Text(f"Vd_fract: {edits.vd_fract}", width=200) , ft.Text(f"K_Factor: {edits.k_factor}", width=200)]) ,
                ft.Row(controls=[
                ft.Text(f"lut_version: {edits.lut_version}", width=200) , ft.Text(f"lut_calibrated: {edits.lut_calibrated}", width=200) ]),
                ft.Row(controls = [
                ft.Text(f"lut_timestamp: {human_timestamp(edits.lut_timestamp)}", width=200) ,  ft.Button("Edit Channel", on_click=edit_channel),])
            ]
            )
        )

 
    #['id_', 'version','version_desc','timestamp', 'capacitor', 'R1', 'R2', 'vd_fract', 'k_factor', 'lut_is_calibrated', 'lut_timestamp']
def ConfigChanForm(config: Chan_Config):
  
    return  ft.Column(
                controls=[
                     ft.Row(controls=[
                         ft.TextField(label = "id_", value= config.id_, on_change=lambda e: setattr(config, "id_", int(e.control.value))),
                         ft.TextField(label="app_id", value=config.app_id, on_change=lambda e: setattr(config, "app_id", int(e.control.value)))]),
                     ft.Row(controls=[
                         ft.TextField(label = "version", value= config.version, on_change=lambda e: setattr(config, "version", int(e.control.value))),
                         ft.TextField(label="version_description", value=config.version_desc , on_change=lambda e: setattr(config, "version_desc", (e.control.value)))]),
                     ft.Row(controls=[
                         ft.TextField(label="timestamp", value =human_timestamp(config.timestamp), on_change=lambda e: setattr(config, "timestamp", float(e.control.value))),
                         ft.TextField(label = "capacitor", value= config.capacitor,   on_change=lambda e: setattr(config, "capacitor", float(e.control.value)))]),
                     ft.Row(controls=[
                         ft.TextField(label="R1", value= config.R1, on_change=lambda e: settattr(config, "R1", int(e.control.value))),
                         ft.TextField(label="R2", value = config.R2, on_change=lambda e: setattr(config, "R2", int(e.control.value)))]),
                     ft.Row(controls=[
                         ft.TextField(label="vd_fract", value= config.vd_fract, on_change=lambda e: settattr(config, "vd_fract", float(e.control.value))),
                         ft.TextField(label="k_factor", value = config.k_factor, on_change=lambda e: settattr(config, "k_factor", float(e.control.value)))]),
                     ft.Row(controls=[
                         ft.TextField(label= "lut_version", value= config.lut_version, on_change=lambda e: settattr(config, "lut_version", int(e.control.value))),
                         ft.TextField(label="lut_is_calibrated", value = config.lut_calibrated, on_change = lambda e: settattr(config, "lut_is_calibrated", int(e.control.value)))]),
                     ft.Row(controls=[
                         ft.TextField(label = "lut_timestamp", value = human_timestamp(config.lut_timestamp), on_change=lambda e: settattr(config, "lut_timestamp", float(e.control.value)))])
                    ]
                )
          

        
# Test Harness, will execute if run  "python chat_config_component.py" in terminal. Will be ignored if imported as a component. So it does not need to be removed or commented out.
@ft.component
def AppView():
    config, set_config = ft.use_state(
        Chan_Config(
            id_=5,
            app_id =1,
            version = 3,
            version_desc = "PCB2",
            timestamp = 1782687301.567499,
            chan= 0,
            chan_desc = "One Cell 3.0-4.5V",
            capacitor = 1.0e-7,       # Need to measure and change accordingly
            R1 = 101100,
            R2 = 303700,
            vd_fract = 0.750247035573123,
            k_factor = 3.0,
            lut_version = 1,
            lut_calibrated= 0,
            lut_timestamp = 1782687301.5675,
        )
    )
    ''' 
    5,1,0,'One Cell 3.0-4.5V',       1,'byResistors',1782687301.5675,1.0e-07,   101100.0,  303700.0,  0.750247035573123,0, 1782687301.5675,3.0
    6,2,1,'Two Cells 6.0-9.0V',     1,'byResistors',1782687301.57536,1.0e-07,  222200.0, 111800.0,  0.334730538922156,0, 1782687301.57536,3.0
    7,3,2,'Three Cells 9.0-13.5V',1,'byResistors',1782687301.58312,1.0e-07,  301400.0, 100700.0,  0.250435215120617,0, 1782687301.58312,3.0
   '''

    return [
    Chan_Config_View(config, set_config)
    ]


ft.run(lambda page: page.render(AppView))
