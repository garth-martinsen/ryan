#file: voltage_row.py

from dataclasses import dataclass

@dataclass
class VoltageRow:
    id_: int
    timestamp: float
    type: str
    chan: int
    vtap: float
    vcell: float

    def __str__(self):
        show= f"id_: {self.id_} timestamp: {self.timestamp} type: {self.type} chan: {self.chan} vtap: {self.vtap} vcell: {self.vcell}"
        return show
'''
example triplet...
{
"SENDER": "SVR",
"RECEIVER": "GUI",
"CODE": 101,
"MSGID": 5123,
"MEAS_ID": 125,
"ROWS": [
{
"id_": 176,
"timestamp": 1783109112,
"type": "c",
"chan": 0,
"vtap": 4.0323,
"vcell": 4.0323
},
{
"id_": 177,
"timestamp": 1783105513,
"type": "c",
"chan": 1,
"vtap": 8.0083,
"vcell": 3.976
},
{
"id_": 178,
"timestamp": 1783105514,
"type": "c",
"chan": 1,
"vtap": 11.9983,
"vcell": 3.99
}
]
}
'''
