# file: message_cfg.py

import struct
from collections import namedtuple
import json

FORMAT = "utf8"
# phoney data for testing
msr_samples =[27657, 27654, 27651, 27653, 27655, 27657, 27651, 27657, 27651, 27655, 27657, 27653, 27656,
                 27658, 27656, 27658, 27657, 27655, 27653, 27655, 27655, 27655, 27655, 27656, 27651, 27658,
                 27656, 27658, 27658, 27653, 27652, 27658, 27658, 27653, 27655, 27657, 27656, 27653, 27654,
                 27656, 27658, 27656, 27655, 27658, 27651, 27651, 27654, 27656, 27651, 27652, 27654, 27655,
                 27655, 27652, 27654, 27658, 27655, 27656, 27658, 27657, 27656, 27657, 27652, 27653]

clb_samples = [[2.01,3.0],[2.02,3.1],[2.1,3.2],[2.15, 3.3],[2.2,3.4],[2.25, 3.5],[2.3,3.6],[2.35,3.6],[2.4,3.7],[2.45,3.8],[2.5,3.9]]
 
Message = namedtuple("Message", ("timestamp", "purpose", "FSR", "LSB", "chan", "mean", "SD", "samples"))

# phoney data for testing 
msr0=Message('2026-2-23  15:31:21.54',100, 4.095, 0.00012496948, 0, 27655.0, 2.2430448, msr_samples)
msr1=Message('2026-2-23  15:31:21.54',100, 4.095, 0.00012496948, 1, 27655.0, 2.2430448, msr_samples)
msr2=Message('2026-2-23  15:31:21.54',100, 4.095, 0.00012496948, 2, 27655.0, 2.2430448, msr_samples)
measures=[msr0,msr1, msr2]

clb0=Message('2026-2-23  15:31:21.54',200,4.095, 0.00012496948, 0, 0,0, clb_samples)
clb1=Message('2026-2-23  15:31:21.54',200,4.095, 0.00012496948, 1, 0,0, clb_samples)
clb2=Message('2026-2-23  15:31:21.54',200,4.095, 0.00012496948, 2, 0,0, clb_samples)
calibs=[clb0,clb1,clb2]
               
 # ws_sockets send strings so the following may not be required.
 
fmt = "<23s 2B 4f 64h"
msg2=json.dumps(measures[0])
msg3=msg2.encode(FORMAT)
print(struct.calcsize(fmt))
