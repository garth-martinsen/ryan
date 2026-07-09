# file: bms_config_component.py
import flet as ft
from bms_classes import BMS_App, BMS_Config

@ft.component
def ConfigView(config: BMS_Config, delete_config) -> ft.Control:
  # Local (transient) editing state—NOT in BMS_Config
  is_editing, set_is_editing = ft.use_state(False)
  new_owner, set_new_owner = ft.use_state(config.owner)
  new_version, set_new_version = ft.use_state(config.version)
  new_chan, set_new_chan = ft.use_state(config.chan)
  new_timestamp, set_new_timestamp = ft.use_state(config.timestamp)
  new_tempC, set_new_tempC = ft.use_state(config.tempC)
  new_adc_fsr, set_new_adc_fsr = ft.use_state(config.adc_fsr)
  new_adc_steps, set_new_adc_steps = ft.use_state(config.adc_steps)
  new_adc_sample_rate, set_new_adc_sample_rate = ft.use_state(config.adc_sample_rate)
  new_capacitor, set_new_capacitor = ft.use_state(config.capacitor)
  new_resistor_1, set_new_resistor_1 = ft.use_state(config.resistor_1)
  new_resistor_2, set_new_resistor_2 = ft.use_state(config.resistor_2)
  new_vd_fract, set_new_vd_fract = ft.use_state(config.vd_fract)
  new_lut_is_calibrated, set_new_lut_is_calibrated = ft.use_state(config.lut_is_calibrated)
  new_lut_timestamp, set_new_lut_timestamp = ft.use_state(config.lut_timestamp)
  new_k_factor, set_new_k_factor = ft.use_state(config.k_factor)
  
  def start_edit():
    set_new_owner(config.owner)
    set_new_version(config.version)
    set_new_chan(config.chan)
    set_new_timestamp(config.timestamp)
    set_new_tempC(config.tempC)
    set_new_adc_fsr(config.adc_fsr)
    set_new_adc_steps(config.adc_steps)
    set_new_adc_sample_rate(config.adc_sample_rate)
    set_new_capacitor(config.capacitor)
    set_new_resistor_1(config.resistor_1)
    set_new_resistor_2(config.resistor_2)
    set_new_vd_fract(config.vd_fract)
    set_new_lut_is_calibrated(config.lut_is_calibrated)
    set_new_lut_timestamp(config.lut_timestamp)
    set_new_k_factor(config.k_factor)
    set_is_echang(True)

  def save():
    config.update( new_owner, new_version, new_chan, new_timestamp, new_tempC, new_adc_fsr, new_adc_steps, new_adc_sample_rate,
                            new_capacitor, new_resistor_1, new_resistor_2, new_vd_fract, new_lut_is_calibrated, new_lut_timestamp, new_k_factor ,)
    set_is_editing(False)

  def cancel():
    set_is_editing(False)

  if not is_editing:
    return ft.Row(
      [
        ft.Text(f"{id} {config.owner} {config.version} {config.chan} {config.timestamp} {config.tempC} {config.adc_fsr} {config.adc_steps} \
                      {config.adc_sample_rate} {config.capacitor} {config.resistor_1} {config.resistor_2} {config.vd_fract} {config.lut_is_calibrated}\
                      {config.lut_timestamp} {config.k_factor} "),
        ft.Button("Edit", on_click=start_edit),
        ft.Button("Delete", on_click=lambda: delete_config(config)),
      ]
    )

  return ft.Row(
    [
      ft.TextField(
        label="owner",
        value=new_owner,
        on_change=lambda e: set_new_owner(e.control.value),
        width=180,
      ),
      ft.TextField(
        label="version",
        value=new_version,
        on_change=lambda e: set_new_timestamp(e.control.value),
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
        label=" tempC",
        value=new_tempC,
        on_change=lambda e: set_new_tempC(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="adc_fsr",
        value=new_adc_fsr,
        on_change=lambda e: set_new_adc_fsr(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="adc_steps",
        value=new_adc_steps,
        on_change=lambda e: set_new_adc_steps(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="adc_sample_rate",
        value=new_adc_sample_rate,
        on_change=lambda e: set_new_adc_sample_rate(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="capacitor",
        value=new_capacitor,
        on_change=lambda e: set_new_capacitor(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="resistor_1",
        value=new_resistor_1,
        on_change=lambda e: set_new_resistor_1(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="resistor_2",
        value=new_resistor_2,
        on_change=lambda e: set_new_resistor_2(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="vd_fract",
        value=new_vd_fract,
        on_change=lambda e: set_new_vd_fract(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="lut_is_calibrated",
        value=new_lut_is_calibrated,
        on_change=lambda e: set_new_lut_is_calibrated(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="lut_timestamp",
        value=new_lut_timestamp,
        on_change=lambda e: set_new_lut_timestamp(e.control.value),
        width=180,
      ),
       ft.TextField(
        label="k_factor",
        value=new_k_factor,
        on_change=lambda e: set_new_k_factor(e.control.value),
        width=180,
      ),
    
      ft.Button("Save", on_click=save),
      ft.Button("Cancel", on_click=cancel),
    ]
  )

@ft.component
def AddConfigForm(add_config) -> ft.Control:
  # Uses local buffers; calls parent action on Add
  new_owner, set_new_owner = ft.use_state("")
  new_version, set_new_version = ft.use_state("")
  new_chan, set_new_chan = ft.use_state("")
  new_timestamp, set_new_timestamp = ft.use_state("")
  new_tempC, set_new_tempC = ft.use_state("")
  new_adc_fsr, set_new_adc_fsr = ft.use_state("")
  new_adc_steps, set_new_adc_steps = ft.use_state("")
  new_adc_sample_rate, set_new_adc_sample_rate = ft.use_state("")
  new_capacitor, set_new_capacitor = ft.use_state("")
  new_resistor_1, set_new_resistor_1 = ft.use_state("")
  new_resistor_2, set_new_resistor_2 = ft.use_state("")
  new_vd_fract, set_new_vd_fract = ft.use_state("")
  new_lut_is_calibrated, set_new_lut_is_calibrated = ft.use_state("")
  new_lut_timestamp, set_new_lut_timestamp = ft.use_state("") 
  new_k_factor, set_new_k_factor = ft.use_state("")


  def add_config_and_clear():
    add_config(new_owner, new_version, new_chan, new_timestamp, new_tempC,new_adc_fsr, new_adc_steps,new_adc_sample_rate,
                new_capacitor,new_resistor_1, new_resistor_2, new_vd_fract, new_lut_is_calibrated, new_lut_timestamp, new_k_factor)
    set_new_owner("")
    set_new_version("")
    set_new_timestamp("")
    set_new_tempC("")
    set_new_adc_fsr("")
    set_new_adc_steps("")
    set_new_adc_sample_rate("")
    set_new_capacitor("")
    set_new_resistor_1("")
    set_new_resistor_2("")
    set_new_vd_fract("")
    set_new_lut_is_calibrated("")
    set_new_lut_timestamp("")
    set_new_k_factor("")
    return ft.Row(
        controls=[
        ft.TextField(
            label="owner",
            width=200,
            value=new_owner,
            on_change=lambda e: set_new_owner(e.control.value),
          ),
        ft.TextField(
            label="versiion",
            width=200,
            value=new_versiion,
            on_change=lambda e: set_new_versiion(e.control.value),
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
            label="tempC",
            width=200,
            value=new_tempC,
            on_change=lambda e: set_new_tempC(e.control.value),
            ),
        ft.TextField(
            label="adc_fsr",
            width=200,
            value=new_adc_fsr,
            on_change=lambda e: set_new_adc_fsr(e.control.value),
            ),
        ft.TextField(
            label="adc_steps",
            width=200,
            value=new_adc_steps,
            on_change=lambda e: set_new_adc_steps(e.control.value),
            ),
        ft.TextField(
            label="adc_sample_rate",
            width=200,
            value=new_adc_sample_rate,
            on_change=lambda e: set_new_adc_sample_rate(e.control.value),
            ),
        ft.TextField(
            label="capacitor",
            width=200,
            value=new_capacitor,
            on_change=lambda e: set_new_capacitor(e.control.value),
            ),
        ft.TextField(
            label="resistor_1",
            width=200,
            value=new_resistor_1,
            on_change=lambda e: set_new_resistor_1(e.control.value),
            ),
        ft.TextField(
            label="resistor_2",
            width=200,
            value=new_resistor_2,
            on_change=lambda e: set_new_resistor_2(e.control.value),
            ),
        ft.TextField(
            label="vd_fract",
            width=200,
            value=new_vd_fract,
            on_change=lambda e: set_new_vd_fract(e.control.value),
            ),
        ft.TextField(
            label="lut_is_calibrated",
            width=200,
            value=new_lut_is_calibrated,
            on_change=lambda e: set_new_lut_is_calibrated(e.control.value),
            ),
        ft.TextField(
            label="lut_timestamp",
            width=200,
            value=new_lut_timestamp,
            on_change=lambda e: set_new_lut_timestamp(e.control.value),
            ),
        ft.TextField(
            label=" k_factor",
            width=200,
            value=new_k_factor,
            on_change=lambda e: set_new_k_factor(e.control.value),
            ),
        ft.Button("Add", on_click=add_config_and_clear),
    ],
  )

@ft.component
def AppView() -> list[ft.Control]:
  app, _ = ft.use_state(
    BMS_App(
      configs=[
        BMS_Config( 5 , 'GM' , 1  , 'Development' , 0 , 'One Cell 3.0-4.5V ' ,       3 , 'PCB2',  1782687301.567499 ,   25.4 , 4.096, 32768 , 64 ,1.0e-07 , 101100.0 , 303700.0 , 0.750247035573123 , 0 , 1782687301.567499 ,   3.0 ),
        BMS_Config( 6 , 'GM' , 1  , 'Development' , 1,  'Two Cells 6.0-9.0V' ,      3 , 'PCB2',  1782687301.57536,      25.4 , 4.096, 32768 , 64, 1.0e-07 , 222200.0 , 111800.0 , 0.334730538922156 , 0 , 1782687301.57536,      3.0 ),
        BMS_Config( 7 , 'GM' , 1  , 'Development' , 2 , 'Three Cells 9.0-13.5V' , 3 , 'PCB2',  1782687301.5831192 , 25.4 , 4.096, 32768 , 64, 1.0e-07 , 301400.0 , 100700.0 , 0.250435215120617 , 0 , 1782687301.5831192 , 3.0 ),
     ]
    )
  )

  return [
    AddConfigForm(app.add_config),
    *[ConfigView(config, app.delete_config) for config in app.configs],
  ]

ft.run(lambda page: page.render(AppView))


