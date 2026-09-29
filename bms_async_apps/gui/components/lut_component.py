# file: bms_lut_component.py   copied from: https://flet.dev/docs/cookbook/declarative-vs-imperative-crud-app/#observables-your-source-of-truth
import flet as ft
from bms_classes import BMS_App, BMS_LUT

'''
class BMS_LUT:
    _id: int
    app_id: int
    version: int
    chan: int
    vm: float
    vin: float
    '''
@ft.component
def LUTView(lut: BMS_LUT, delete_lut) -> ft.Control:
    # Local (transient) editing state—NOT in BMS_LUT
    is_editing, set_is_editing = ft.use_state(False)
    new_version, set_new_version = ft.use_state(lut.version)
    new_chan, set_new_chan = ft.use_state(lut.chan)    
    new_vm, set_new_vm = ft.use_state(lut.vm)    
    new_vin, set_new_vin = ft.use_state(lut.vin)    
 
def start_edit():
    set_new_version(lut.version)
    set_new_chan(lut.chan)
    set_new_vm(lut.vm)
    set_new_vin(lut.vin)

def save():
    lut.update( new_version,  new_chan,  new_vm, new_vin )
    set_is_editing(False)
    
def cancel():
    set_is_editing(False)
    if not is_editing:
        return ft.Row(
      [
        ft.Text(f" {lut._id}  {lut.app_id}  {lut.version}  {chan}  {vm}  {vin} "),
        ft.Button("Edit", on_click=start_edit),
        ft.Button("Delete", on_click=lambda: delete_record(record)),
      ]
    )

    return ft.Row(
    [
     ft.TextField(
        label=" _id",
        value=new__id,
        on_change=lambda e: set_new__id(e.control.value),
        width=180,
      ),
        ft.TextField(
        label="app_id",
        value=new_app_id,
        on_change=lambda e: set_new_app_id(e.control.value),
        width=180,
      ),
      ft.TextField(
        label="version",
        value=new_version,
        on_change=lambda e: set_new_version(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="chan",
        value=new_chan,
        on_change=lambda e: set_new_chan(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="vm",
        value=new_vm,
        on_change=lambda e: set_new_vm(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="vin",
        value=new_vin,
        on_change=lambda e: set_new_vin(e.control.value),
        width=180,
      ),
      ft.Button("Save", on_click=save),
      ft.Button("Cancel", on_click=cancel),
    ]
  )

@ft.component
def AddLUTForm(add_lut) -> ft.Control:
  # Uses local buffers; calls parent action on Add
  new_id, set_new_id  = ft.use_state("")
  new_app_id, set_new_app_id = ft.use_state("")
  new_version, set_new_version = ft.use_state("")
  new_chan, set_new_chan = ft.use_state("")
  new_vm, set_new_vm = ft.use_state("")
  new_vin, set_new_vin = ft.use_state("")

  def add_lut_and_clear():
    add_lut(new__id, new_app_id, new_version, new_chan, new_vm,  new_vin)
    set_new__id("")
    set_new_app_id("")
    set_new_version("")
    set_new_chan("")
    set_new_vm("")
    set_new_vin("")
    return ft.Row(
        controls=[
        ft.TextField(
            label="_id",
            width=200,
            value=new__id,
            on_change=lambda e: set_new__id(e.control.value),
            ),
        ft.TextField(
            label="app_id",
            width=200,
            value=new_app_id,
            on_change=lambda e: set_new_app_id(e.control.value),
            ),
        ft.TextField(
            label="version",
            width=200,
            value=new_version,
            on_change=lambda e: set_new_version(e.control.value),
          ),
        ft.TextField(
            label="chan",
            width=200,
            value=new_chan,
            on_change=lambda e: set_new_chan(e.control.value),
            ),
     ft.TextField(
            label="vm",
            width=200,
            value=new_vm,
            on_change=lambda e: set_new_vm(e.control.value),
            ),
        ft.TextField(
            label="vin",
            width=200,
            value=new_vin,
            on_change=lambda e: set_new_vin(e.control.value),
            ),
         ft.Button("Add", on_click=add_record_and_clear),
    ],
  )

@ft.component
def AppView() -> list[ft.Control]:
  app, _ = ft.use_state(
    BMS_App(
      luts=[
                      BMS_LUT(1 , 1 , 3 , 0 , 2.2507 , 3.0 ),
                      BMS_LUT(  2 , 1 , 3 , 0 , 2.3258 , 3.1 ),
                      BMS_LUT( 3 , 1 , 3 , 0 , 2.4008 , 3.2 ),
                      BMS_LUT( 4 , 1 , 3 , 0 , 2.4758 , 3.3 ),
                      BMS_LUT(  5 , 1 , 3 , 0 , 2.5508 , 3.4 ),
                      BMS_LUT(  6 , 1 , 3 , 0 , 2.6259 , 3.5  ),
  ]
    )
  )

  return [
    AddLUTForm(app.add_lut),
    *[LUTView(lut, app.delete_lut) for lut in app.luts],
  ]

ft.run(lambda page: page.render(AppView))

 