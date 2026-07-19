#file: calibrate_component.py

import flet as ft
from dataclasses import dataclass
import time
from copy import deepcopy

# an x_component.py will contain: dataclass, view, form, test_harness (AppView)

@ft.observable
@dataclass

class CalibRecord:
    id_: int
    app_id: int
    version: int
    version_desc:str
    timestamp: float
    chan: int
    chan_desc: str
    vin: float
    vb: float
    error: float
    slope: float  
    intercept: float
  

def human_timestamp( tm:float):
    return time.asctime(time.localtime(tm))                    

@ft.component
def CalibRecord_View(calib_record: CalibRecord, set_calib_record):
    print(f"Rendering CalibRecord_View id:  {id(calib_record)},  vin: {calib_record.vin}")
    edits = deepcopy(calib_record)

    def update_error(e):
        edits.error = edits.vin - edits.vb
        
    
    def close_dialog(e):
        print("called close_dialog()")
        # Close the dialog 
        ft.context.page.pop_dialog()
        
    def edit_channel(e):
        print(f"entered handler for edit_calib_record with {e}")
        print(f"calib_record: {calib_record}")
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Calibration Record"),
            content=CalibRecordForm(edits),
            actions=[ ft.Button("Save", on_click=save_channel ), ft.Button("Cancel", on_click=close_dialog ) ] )

        ft.context.page.show_dialog(dlg)
        
    def save_channel(e):
        print("save_channel was called.")   
        print(f"edits : {edits}, calib_record: {calib_record}")
        print(f"edits.__dict__ : {edits.__dict__}")
        # update calib_record from edits
        print("calib_record id:", id(calib_record))
        set_calib_record(edits)
        print(f"after updating calib_record from edits:  {calib_record}")
        close_dialog(e)
           
    def cancel_channel(e):
        print("cancel_common was called.")
        close_dialog(e)
  
    return ft.Card(
        content=ft.Column(
            controls=[
                ft.Row(controls=[
                ft.Text(f"id_: {calib_record.id_}",   width=200), ft.Text(f"App_id: {edits.app_id}",  width=200),]),
                 ft.Row(controls=[
                ft.Text(f"version: {edits.version}", width=200), ft.Text(f"Version_description: {edits.version_desc}", width=200)]),               
                ft.Row(controls=[
                ft.Text(f"Channel: {edits.chan}", width=200), ft.Text(f"Channel_description: {edits.chan_desc}", width=200)]),
                ft.Row(controls=[
                ft.Text(f"timestamp: {human_timestamp(edits.timestamp)}", width=200), ft.Text(f"Vin: {edits.vin}", width=200)]) ,
                ft.Row(controls=[
                ft.Text(f"Vb: {edits.vb}", width=200) , ft.Text(f"Vb: {edits.vb}", width=200)]) ,
                ft.Row(controls=[
                ft.Text(f"Error: {edits.error}", width=200) , ft.Text(f"Error: {edits.error}", width=200)]) ,
                ft.Row(controls=[
                ft.Text(f"Slope: {edits.slope}", width=200) , ft.Text(f"Slope: {edits.slope}", width=200) ]),
                ft.Row(controls = [
                ft.Text(f"Intercept: {edits.intercept}", width=200) ,  ft.Button("Edit CalibRecord", on_click=edit_channel),])
            ]
            )
        )

 
def CalibRecordForm(edits: CalibRecord):
  
    return  ft.Column(
                controls=[
                     ft.Row(controls=[
                         ft.TextField(label = "id_", value= edits.id_, on_blur=lambda e: setattr(edits, "id_", int(e.control.value))),
                         ft.TextField(label="app_id", value=edits.app_id, on_blur=lambda e: setattr(edits, "app_id", int(e.control.value)))]),
                     ft.Row(controls=[
                         ft.TextField(label = "version", value= edits.version, on_blur=lambda e: setattr(edits, "version", int(e.control.value))),
                         ft.TextField(label="version_description", value=edits.version_desc , on_blur=lambda e: setattr(edits, "version_desc", (e.control.value)))]),
                     ft.Row(controls=[
                         ft.TextField(label="timestamp", value =human_timestamp(edits.timestamp), on_blur=lambda e: setattr(edits, "timestamp", float(e.control.value))),
                        ft.TextField(label = "Vin", value= edits.vin,   on_blur=lambda e: setattr(edits, "vin", float(e.control.value)) )]),
                     ft.Row(controls=[
                         ft.TextField(label="Vb", value= edits.vb, on_blur=lambda e: setattr(edits, "Vb", int(e.control.value))),
                         ft.TextField(label="Error", value = edits.error, on_blur=lambda e: setattr(edits, "Error", int(e.control.value)))]),
                     ft.Row(controls=[
                         ft.TextField(label="Slope", value= edits.slope, on_blur=lambda e: setattr(edits, "slope", float(e.control.value))),
                         ft.TextField(label="Intercept", value = edits.intercept, on_blur=lambda e: setattr(edits, "k_factor", float(e.control.value)))]),
                    ]
                )
          

        
# Test Harness, will execute if run  "python chat_config_component.py" in terminal. Will be ignored if imported as a component. So it does not need to be removed or commented out.
@ft.component
def AppView():
    calib_record, set_calib_record = ft.use_state(
        CalibRecord(
            id_=5,
            app_id =1,
            version = 3,
            version_desc = "PCB2",
            timestamp = 1782687301.567499,
            chan= 0,
            chan_desc = "One Cell 3.0-4.5V",
            vin = 4.094,       # Need to measure and change accordingly
            vb = 4.0939,
            error = 0.0001,
            slope = 1.33289430358907 ,
            intercept = 0.024164327787965,
        )
    )
    ''' 
      SLOPE       │     intercept      │
├──────────────────┼────────────────────┤
│ 1.33289430358907 │ 0.024164327787965  │
│ 2.98747763864043 │ 0.0498818752307106 │
│ 3.99304865938431 │ 0.0641294273419395
'''

    return [
    CalibRecord_View(calib_record, set_calib_record)
    ]


ft.run(lambda page: page.render(AppView))

