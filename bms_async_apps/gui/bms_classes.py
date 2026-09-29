# file: bms_classes.py
from dataclasses import dataclass, field
import flet as ft

# ID,OWNER ,APP_ID, APP_DESC,  CHAN, CHAN_DESC, version , VERSION_DESC, TIMESTAMP,  TEMPC ,  ADC_FSR , 
# ADC_STEPS ,  ADC_SAMPLE_RATE,  C1,   R1,   R2,  VD_FRACT,  LUT_CALIBRATED, LUT_TS,  K_FACTOR
#TODO 1: change vd_fract field to : slope
#TODO 2: add field : intercept: float
@ft.observable
@dataclass
class App_Config:
    _id:int
    owner: str
    app_id:int
    app_desc: str
    version: int
    version_desc: str
    timestamp: float
    tempC:float
    adc_fsr:float
    adc_steps: int
    adc_sample_rate: int
    
    def update(self, app_config: App_Config):
        self.timestamp =bms_config.timestamp
        self.tempC=bms_config.tempC
        self.adc_fsr = bms_config.adc_fsr
        self.adc_steps = bms_config.adc_steps
        self.adc_sample_rate = bms_config.adc_sample_rate


 
@ft.observable
@dataclass
#ID  ,  MSGID ,  VERSION ,    TIMESTAMP   , TYPE , CHAN ,   A2D_MEAN   , VM_MEAN ,  VM_SD  ,  VB  ,  VIN ,    ERROR    , SAMP_SZ , DISCARD_SZ , KEEP_SZ 

#ID  │ APP_ID │ VERSION │ CHAN │   VM   │ VIN  │    

        
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

