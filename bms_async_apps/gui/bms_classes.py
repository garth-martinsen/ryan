# file: bms_classes.py
from dataclasses import dataclass, field
import flet as ft

# ID,OWNER ,APP_ID, APP_DESC,  CHAN, CHAN_DESC, version , VERSION_DESC, TIMESTAMP,  TEMPC ,  ADC_FSR , 
# ADC_STEPS ,  ADC_SAMPLE_RATE,  C1,   R1,   R2,  VD_FRACT,  LUT_CALIBRATED, LUT_TS,  K_FACTOR
#TODO 1: change vd_fract field to : slope
#TODO 2: add field : intercept: float
@ft.observable
@dataclass
class BMS_Config:
    _id:int
    owner: str
    app_id:int
    app_desc: str
    chan:int
    chan_desc: str
    version: int
    version_desc: str
    timestamp: float
    tempC:float
    adc_fsr:float
    adc_steps: int
    adc_sample_rate: int
    capacitor: float
    resistor_1: float
    resistor_2: float
    vd_fract: float     
    lut_is_calibrated: int
    lut_timestamp: float
    k_factor: float
    
    def update(self, bms_config: BMS_Config):
        self.chan= bms_config.chan
        self.timestamp =bms_config.timestamp
        self.tempC=bms_config.tempC
        self.adc_fsr = bms_config.adc_fsr
        self.adc_steps = bms_config.adc_steps
        self.adc_sample_rate = bms_config.adc_sample_rate
        self.capacitor = bms_config.capacitor
        self.resistor_1 = bms_config.resistor_1
        self.resistor_2: bms_config.resister_2
        self.a2d_mean = bms_config.a2d_mean
        self.vd_fract = bms_config.vd_fract    
        self.lut_is_calibrated = bms_config.lut_is_calibrated
        self.lut_timestamp = bms_config.lut_timestamp
        self.k_factor = bms_config.k_factor


 
@ft.observable
@dataclass
#ID  ,  MSGID ,  VERSION ,    TIMESTAMP   , TYPE , CHAN ,   A2D_MEAN   , VM_MEAN ,  VM_SD  ,  VB  ,  VIN ,    ERROR    , SAMP_SZ , DISCARD_SZ , KEEP_SZ 
class BMS_Record:
   _id : int
   msgid: int
   version: int
   timestamp: float
   type : str
   chan: int
   a2d_mean: float
   vm_mean: float
   vm_sd : float
   vb : float
   vin: float
   error: float
   samp_sz: int
   discard_sz : int
   keep_sz : int
   
   def update(self, bms_record: BMS_Record):
       self. msgid =  bms_record.msgid
       self.version = bms_record.version
       self.timestamp =bms_record.timestamp
       self.type = bms_record.type
       self.chan = bms_record.chan
       self.a2d_mean = bms_record.a2d_mean
       self.vm_mean = bms_record.vm_mean
       self.vm_sd = bms_record.vm_sd
       self.vb = bms_record.vb
       self.vin= bms_record.vin
       self.error= bms_record.error
       self.samp_sz= bms_record.samp_sz
       self.discard_sz = bms_record.discard_sz
       self.keep_sz = bms_record.keep_sz
       

#ID  │ APP_ID │ VERSION │ CHAN │   VM   │ VIN  │    
@ft.observable
@dataclass
class BMS_LUT:
    _id: int
    app_id: int
    version: int
    chan: int
    vm: float
    vin: float
    
    def update(self, bms_lut: BMS_LUT):
        self. _id = bms_lut._id
        self.app_id= bms_lut.app_id
        self.version= bms_lut.version
        self.chan= bms_lut.chan
        self.vm= bms_lut.vm
        self.vin= bms_lut.vin
        
        
@ft.observable
@dataclass
class BMS_App:
    configs: list[BMS_Config]
    luts: list[BMS_LUT]
    records: list[BMS_Record]
    
    configs: list[BMS_Config] = field(default_factory=list)
    luts: list[BMS_LUT] = field(default_factory=list)
    records: list[BMS_Record] = field(default_factory=list)

    def add_config(self, bms_config: BMS_Config):
            self.configs.append(BMS_Config(bms_config))

    def delete_config(self, config:BMS_Config):
        self.users.remove(config)

    def add_lut(self, bms_lut: BMS_LUT):
            self.luts.append(BMS_LUT(bms_lut))

    def delete_lut(self, bms_lut:BMS_LUT):
        self.users.remove(bms_lut)

    def add_record(self, bms_record: BMS_Record):
            self.records.append(BMS_Record(bms_record))

    def delete_record(self, bms_record:BMS_Record):
        self.records.remove(bms_record)

