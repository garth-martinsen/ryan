#file: test_line_parm_estimator.py
import sys
sys.path.append("/Users/garth/DEV/ryan/bms_async_apps")  # project dir

from svr.line_parm_estimator import LineParmEstimator as LPE
import pytest

# methods to be tested...
#   def __init__(self):
#    def compute_line_parms(self):
#    def compute_line_parms_for_chan(self, chan, points):
#    def limits(self):
#    def estimate_vb(self, chan, vm):

def test_init():
    lpe = LPE()
    assert [len(x) for x in lpe.points] == [0,0,0],  'line_parms_estimator should not have points until compute_line_parms() completes.'
    assert [len(x) for x in lpe.slopes] == [0,0,0],  'line_parms_estimator should not have slopes until compute_line_parms() completes.'
    assert [len(x) for x in lpe.intercepts]==[0,0,0],'line_parms_estimator should not have intercepts until compute_line_parms() completes.'
    print("PASSED test_init()")
    
def test_compute_line_parms():
    lpe = LPE()
    lpe.compute_line_parms()
    #for i in range(3):
        #print(f" chan : {i}  points: { len(lpe.points[i]) }  slope: {lpe.slopes[i]}  intrcpt: {lpe.intercepts[i]}")
    assert len(lpe.points[0])== 16, "There should be 16 points in chan 0."
    assert len(lpe.points[1])== 31, "There should be 31 points in chan 0."
    assert len(lpe.points[2])== 46, "There should be 16 points in chan 0."
    assert lpe.slopes[0] == 1.332883803048778, " Slope is wrong: "
    assert lpe.slopes[1] == 2.9874658669851355 , " Slope is wrong: "
    assert lpe.slopes[2] == 3.993047659001258 , " Slope is wrong: "
    assert lpe.intercepts[0] == 3.138640749167365e-05, " Intercept is wrong: "
    assert lpe.intercepts[1] == 2.4762853823381925e-05, " Intercept is wrong: "
    assert lpe.intercepts[2] == 4.886606634697629e-06, " Intercept is wrong: "
 
    print("PASSED test_compute_line_parms()")
 
def test_estimate_vb_inbounds():
    lpe = LPE()
    lpe.compute_line_parms()
    vb=lpe.estimate_vb(0,2.45)
    assert vb == 3.265596703876998
    vb=lpe.estimate_vb(1,2.45)
    assert vb == 7.319316136967406, f"should be: vb {vb}"
    vb=lpe.estimate_vb(2,2.45)
    assert vb == 9.782971651159716, f"should be vb {vb}"
    
    print("PASSED test_estimate_vb_inbounds()")

def test_estimate_vb_outofbounds():
    lpe = LPE()
    lpe.compute_line_parms()
    try:
           vb=lpe.estimate_vb(0,1.45)
    except ValueError as err:
        print(err)
    try:
           vb=lpe.estimate_vb(1,1.45)
    except ValueError as err:
        print(err)
   
    try:
           vb=lpe.estimate_vb(2,1.45)
    except ValueError as err:
        print(err)
 
    print("PASSED test_estimate_vb_outofbounds()")