
#file: /gui/components/app_config.py

import flet as ft
from dataclasses import dataclass
import time
from copy import deepcopy

# an x_component.py will contain: dataclass, view, form, test_harness (AppView)

@ft.observable
@dataclass
class AppConfig:
    id_: int
    owner : str
    app_desc: str
    timestamp: float
    tempC: float
    adc_fsr : float
    adc_steps: int
    adc_sample_rate: int
    version: int
    version_desc:str
    

def human_timestamp( tm:float):
    return time.asctime(time.localtime(tm))                    

def AppConfigView(config: AppConfig, set_configs):
    # print("Rendering Chan_Config_View", id(edits), edits.capacitor)
    edits = deepcopy(config)
    def close_dialog(e):
        print("called close_dialog()")
        # Close the dialog 
        ft.context.page.pop_dialog()
        
    def edit_channel(e):
        print(f"entered handler for edit_app with {e}")
        print(f"edits: {edits}")
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Application Configuration"),
            content=AppConfigForm(edits),
            actions=[ ft.Button("Save", on_click=save_channel ), ft.Button("Cancel", on_click=close_dialog ) ] )

        ft.context.page.show_dialog(dlg)
        
    def save_channel(e):
        print("save_app_config was called.")   
        print(f"edits : {edits}, edits: {edits}")
        # update config from edits
        set_configs(edits)
        close_dialog(e)
           
    def cancel_app_config(e):
        print("cancel_app_config  was called.")
        close_dialog(e)
  
    return ft.Card(
        content=ft.Column(
            controls=[
                ft.Row(controls=[
                    ft.Text(f"id_: {edits.id_}",   width=200), 
                    ft.Text(f"Owner : {edits.owner}", width=200), 
                ]),
                ft.Row(controls=[
                    ft.Text(f"app_description: {edits.app_desc}", width=200),               
                    ft.Text(f"timestamp: {human_timestamp(edits.timestamp)}", width=200), 
                ]),
                ft.Row(controls=[
                    ft.Text(f"Temperature ºC : {edits.tempC}", width=200) ,
                    ft.Text(f"ADC_FSR : {edits.ADC_FSR}", width=200) , 
                ]),
                ft.Row(controls=[
                    ft.Text(f"ADC_STEPS: {edits.ADC_STEPS}", width=200) ,
                    ft.Text(f"ADC_SAMPLE_RATE: {edits.ADC_SAMPLE_RATE}", width=200) , 
                ]),
                ft.Row(controls=[
                    ft.Text(f"version: {edits.version}", width=200) , 
                    ft.Text(f"Version description: {edits.version_desc}", width=200) ,
                ]),
        ]))

 

def AppConfigForm(edits: Chan_Config):
    return  ft.Column(
        controls=[
             ft.Row(controls=[ 
                 ft.TextField(label = "id_", value= edits.id_, on_blur=lambda e: setattr(edits, "id_", int(e.control.value))),
                 ft.TextField(label="Owner", value= edits.owner, on_blur=lambda e: setattr(edits, "owner", (e.control.value)))]),
             ft.Row(controls=[
                 ft.TextField(label = "App Description: ", value= edits.app_desc, on_blur=lambda e: setattr(edits, "version", int(e.control.value))),
                 ft.TextField(label="timestamp", value =edits.timestamp, on_blur=lambda e: setattr(edits, "timestamp", float(e.control.value))),
             ft.Row(controls=[
                 ft.TextField(label="Temperature ºC:", value= edits.tempC, on_blur=lambda e: setattr(edits, "Temperature", float (e.control.value))),
                 ft.TextField(label="ADC_FSR", value = edits.ADC_FSR, on_blur=lambda e: setattr(edits, "ADC_FSR:", float(e.control.value)))]),
             ft.Row(controls=[
                 ft.TextField(label="ADC_STEPS", value= edits.ADC_STEPS, on_blur=lambda e: setattr(edits, "ADC_STEPS", int(e.control.value))),
                 ft.TextField(label="ADC_SAMPLE_RATE", value = edits.ADC_SAMPLE_RATE, on_blur=lambda e: setattr(edits, "ADC_SAMPLE_RATE", int(e.control.value)))]),
             ft.Row(controls=[
                 ft.TextField(label= "Version", value= edits.version, on_blur=lambda e: setattr(edits, "Version", int(e.control.value))),
                 ft.TextField(label="Version Description", value = edits.version_desc, on_blur = lambda e: setattr(edits, "version_desc", str(e.control.value)))]),
                    ]
                )])
          

