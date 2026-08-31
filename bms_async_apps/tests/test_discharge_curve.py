from services.discharge_curve import discharge_curve, Interpolator
import pytest

interpolator = Interpolator()
discharge_curve = discharge_curve

''' The discharge curve works for a single cell LiIon. Some study will be needed to use it for a 3 Cell battery pack...'''
def test_discharge_curve():
     '''discharge table V vs ah_used is for a single LiIon cell. Each cell has its own discharge_curve. Does table have 11 entries. Does 1980 ahu => 3.4V? '''
     assert len(discharge_curve) == 11, f"There should be {len(discharge_curve)}"  
     assert discharge_curve[1980] == 3.4, f"The battery voltage when 1980 amp_hrs have been expended should be {3.4}"

def test_interpolator():
    '''For values not falling on ahu values in table, need to interpolate.  Testing ahu of 1985 and 1332 '''
    assert interpolator.interpolate(1985) == 3.35 , f"Interpolation of 1985 should yield vb = {3.35}"
    assert interpolator.interpolate(1332) == 3.6771428571428575 , f"Interpolation of 1985 should yield vb = {3.6771428571428575}"
    
def test_interpolator_out_of_bounds():
    '''When ahu values fall outside of table boundaries, show error '''
    with pytest.raises( UnboundLocalError):
        assert interpolator.interpolate(-100) ==  UnboundLocalError , f"Interpolation of -100 should raise error{ UnboundLocalError }"
        assert interpolator.interpolate(2500) ==  UnboundLocalError, f"Interpolation of 2500 should raise error{ UnboundLocalError }"
