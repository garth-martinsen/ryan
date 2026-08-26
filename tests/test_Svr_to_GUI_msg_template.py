from common.templates.svr_templates  import VOLTAGE_REPORT_TEMPLATE 
from copy import deepcopy

test_msg=deepcopy(VOLTAGE_REPORT_TEMPLATE)
print(f"test_msg : {test_msg}")

def test_SENDER():
    sender = test_msg["SENDER"]
    assert sender == "SVR", f"The sender should be {sender}"

def test_RECEIVER():
    receiver = test_msg["RECEIVER"]
    assert receiver == "GUI", f"The receiver should be {receiver}"

def test_CODE():
    code = test_msg["CODE"]
    assert code == 101, f"The code should be {code}"

def test_ROWS():
    rows = test_msg["ROWS"]    
    assert len(rows) == 4, 'There should be 4 rows.Three Voltage rows plus 1 current row.'
    assert len(rows[0]) == 6, f"The row should contain {len(rows[0])} items."
'''
{ "id_": 2, "timestamp": 1783105513.0, "type": "c", "chan": 1, "vcell": 3.97, "vtap": 7.98 },
'''
def test_row_contents():
    rows=[]
    rows = test_msg["ROWS"]
    row = rows[1]
    assert row["ID_"]== 2 , f"The row.id should be {2} ."
    assert row["TIMESTAMP"]== 1783105513.0, f"The row.timestamp should be  {1783105513.0} ."
    assert row["TYPE"]== "c", f"The type should be {'c'} ."
    assert row["CHAN"]== 1, f"The chan should be {1} ."
    assert row["VTAP"]== 7.999, f"The vtap should be {7.98} ."
    assert row["VCELL"]== 3.976, f"The vcell should be {3.976} ."

