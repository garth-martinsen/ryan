# file: bms_record_component.py
import flet as ft
from bms_classes import BMS_App, BMS_Record

@ft.component
def RecordView(record: BMS_Record, delete_record) -> ft.Control:
    # Local (transient) editing state—NOT in BMS_Record
    is_editing, set_is_editing = ft.use_state(False)
    new_version, set_new_version = ft.use_state(record.version)
    new_timestamp, set_new_timestamp = ft.use_state(record.timestamp)
    new_type, set_new_type = ft.use_state(record.type)
    new_chan, set_new_chan = ft.use_state(record.chan)
    new_a2d_mean, set_new_a2d_mean = ft.use_state(record.a2d_mean)
    new_vm_mean, set_new_vm_mean = ft.use_state(record.vm_mean)
    new_vm_sd, set_new_vm_sd = ft.use_state(record.vm_sd)
    new_vb, set_new_vb = ft.use_state(record.vb)
    new_vin, set_new_vin = ft.use_state(record.vin)
    new_error, set_new_error = ft.use_state(record.error)
    new_samp_sz, set_new_samp_sz = ft.use_state(record.samp_sz)
    new_discard_sz, set_new_discard_sz = ft.use_state(record.discard_sz)
    new_keep_sz, set_new_keep_sz = ft.use_state(record.keep_sz)   
 
def start_edit():
    set_new_version(record.version)
    set_new_chan(record.chan)
    set_new_timestamp(record.timestamp)
    set_new_a2d_mean(record.a2d_mean)
    set_new_vm_mean(record.vm_mean)
    set_new_vm_sd(record.vm_sd)
    set_new_vb(record.vb)
    set_new_vin(record.vin)
    set_new_error(record.error)
    set_new_samp_sz(record.samp_sz)
    set_new_discard_sz(record.discard_sz)
    set_new_keep_sz(record.keep_sz)
    set_is_echang(True)

def save():
    record.update( new_version, new_type, new_timestamp, new_chan,new_a2d_mean, new_vm_mean, new_vm_sd, new_vb,
                            new_vin, new_error, new_samp_sz, new_discard_sz, new_keep_sz,)
    set_is_editing(False)

def cancel():
    set_is_editing(False)
    if not is_editing:
        return ft.Row(
      [
        ft.Text(f"{_id} {version} {version} {chan} {timestamp} {a2d_mean} {vm_mean} {vm_sd} {vb} {vin} {error} {samp_sz} {discard_sz} {keep_sz}"),
        ft.Button("Edit", on_click=start_edit),
        ft.Button("Delete", on_click=lambda: delete_record(record)),
      ]
    )

    return ft.Row(
    [
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
        label="timestamp",
        value=new_timestamp,
        on_change=lambda e: set_new_timestamp(e.control.value),
        width=180,
      ),
       ft.TextField(
        label=" a2d_mean",
        value=new_a2d_mean,
        on_change=lambda e: set_new_a2d_mean(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="vm_mean",
        value=new_vm_mean,
        on_change=lambda e: set_new_vm_mean(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="vm_sd",
        value=new_vm_sd,
        on_change=lambda e: set_new_vm_sd(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="vb",
        value=new_vb,
        on_change=lambda e: set_new_vb(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="vin",
        value=new_vin,
        on_change=lambda e: set_new_vin(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="error",
        value=new_error,
        on_change=lambda e: set_new_error(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="samp_sz",
        value=new_samp_sz,
        on_change=lambda e: set_new_samp_sz(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="discard_sz",
        value=new_discard_sz,
        on_change=lambda e: set_new_discard_sz(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="keep_sz",
        value=new_keep_sz,
        on_change=lambda e: set_new_keep_sz(e.control.value),
        width=180,
      ),  
      ft.Button("Save", on_click=save),
      ft.Button("Cancel", on_click=cancel),
    ]
  )

@ft.component
def AddRecordForm(add_record) -> ft.Control:
  # Uses local buffers; calls parent action on Add
  new_version, set_new_version = ft.use_state("")
  new_chan, set_new_chan = ft.use_state("")
  new_timestamp, set_new_timestamp = ft.use_state("")
  new_a2d_mean, set_new_a2d_mean = ft.use_state("")
  new_vm_mean, set_new_vm_mean = ft.use_state("")
  new_vm_sd, set_new_vm_sd = ft.use_state("")
  new_vb, set_new_vb = ft.use_state("")
  new_vin, set_new_vin = ft.use_state("")
  new_error, set_new_error = ft.use_state("")
  new_samp_sz, set_new_samp_sz = ft.use_state("")
  new_discard_sz, set_new_discard_sz = ft.use_state("")
  new_keep_sz, set_new_keep_sz = ft.use_state("")

  def add_record_and_clear():
    add_record(new_version, new_version, new_chan, new_timestamp, new_a2d_mean,new_vm_mean, new_vm_sd,new_vb,
                new_vin,new_error, new_samp_sz, new_discard_sz, new_keep_sz, new_lut_timestamp, new_k_factor)
    set_new_version("")
    set_new_version("")
    set_new_timestamp("")
    set_new_a2d_mean("")
    set_new_vm_mean("")
    set_new_vm_sd("")
    set_new_vb("")
    set_new_vin("")
    set_new_error("")
    set_new_samp_sz("")
    set_new_discard_sz("")
    set_new_keep_sz("")
    set_new_lut_timestamp("")
    set_new_k_factor("")
    return ft.Row(
        controls=[
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
            label="timestamp",
            width=200,
            value=new_timestamp,
            on_change=lambda e: set_new_timestamp(e.control.value),
            ),
        ft.TextField(
            label="a2d_mean",
            width=200,
            value=new_a2d_mean,
            on_change=lambda e: set_new_a2d_mean(e.control.value),
            ),
        ft.TextField(
            label="vm_mean",
            width=200,
            value=new_vm_mean,
            on_change=lambda e: set_new_vm_mean(e.control.value),
            ),
        ft.TextField(
            label="vm_sd",
            width=200,
            value=new_vm_sd,
            on_change=lambda e: set_new_vm_sd(e.control.value),
            ),
        ft.TextField(
            label="vb",
            width=200,
            value=new_vb,
            on_change=lambda e: set_new_vb(e.control.value),
            ),
        ft.TextField(
            label="vin",
            width=200,
            value=new_vin,
            on_change=lambda e: set_new_vin(e.control.value),
            ),
        ft.TextField(
            label="error",
            width=200,
            value=new_error,
            on_change=lambda e: set_new_error(e.control.value),
            ),
        ft.TextField(
            label="samp_sz",
            width=200,
            value=new_samp_sz,
            on_change=lambda e: set_new_samp_sz(e.control.value),
            ),
        ft.TextField(
            label="discard_sz",
            width=200,
            value=new_discard_sz,
            on_change=lambda e: set_new_discard_sz(e.control.value),
            ),
        ft.TextField(
            label="keep_sz",
            width=200,
            value=new_keep_sz,
            on_change=lambda e: set_new_keep_sz(e.control.value),
            ),
     ft.Button("Add", on_click=add_record_and_clear),
    ],
  )

@ft.component
def AppView() -> list[ft.Control]:
  app, _ = ft.use_state(
    BMS_App(
      records=[
                      BMS_Record( 1, 5078,   3, 1782687301.57536,      'm'  , 0  , 24207.4516,   3.0259, 6.221e-05,  4.0332, 0.0 ,   -4.0332 ,  64,     2 ,        62  ),
                      BMS_Record( 2, 5078,   3, 1782687301.57536  ,    'm' ,  1  , 21355.0,         2.6687 , 0.0 ,            7.9728 , 0.0 ,  -7.9728 ,  64,     2 ,        62  ),
                      BMS_Record( 3, 5078,   3 , 1782687301.57536 ,    'm'  , 2  , 24212.0,         3.0265, 0.0 ,             12.085, 0.0 ,   -12.085  , 64,     1 ,        63  ),
                      BMS_Record( 83, 5044, 3  , 1782687301.57536 ,   'c'  , 0  ,  24241.0   ,      3.0301 , 0.0 ,            4.0388 , 4.062 , 0.0232, 64 ,    2 ,        62  ),
                      BMS_Record( 84, 5044, 3  , 1782687301.57536 ,   'c'  , 1  ,  21458.0   ,      2.6823 , 0.0  ,           8.0133 , 8.05 ,   0.0367, 64 ,    1,         63  ),
                      BMS_Record( 85, 5044, 3  , 1782687301.57536 ,   'c'  , 2  ,  24212.08 ,      3.0265 , 3.379e-05, 12.085 , 12.14 , 0.055,   64 ,    1,         63  ),
  ]
    )
  )

  return [
    AddRecordForm(app.add_record),
    *[RecordView(record, app.delete_record) for record in app.records],
  ]

ft.run(lambda page: page.render(AppView))


