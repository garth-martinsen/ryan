from services.discharge_curve import discharge_curve, Interpolator
import pytest

interpolator = Interpolator()
discharge_curve = discharge_curve


def test_discharge_curve():
     assert len(discharge_curve) == 11, f"There should be {len(discharge_curve)}"  
     assert discharge_curve[1980] == 3.4, f"The battery voltage when 1980 amp_hrs have been expended should be {3.4}"

def test_interpolator():
     assert interpolator.interpolate(1985) == 3.35 , f"Interpolation of 1985 should yield vb = {3.35}"
     assert interpolator.interpolate(1332) == 3.6771428571428575 , f"Interpolation of 1985 should yield vb = {3.6771428571428575}"
    
def test_interpolator_out_of_bounds():
     with pytest.raises( UnboundLocalError):
          assert interpolator.interpolate(-100) ==  UnboundLocalError , f"Interpolation of 1985 should yield vb = {3.35}"
          assert interpolator.interpolate(2500) == 3.6771428571428575 , f"Interpolation of 1985 should yield vb = {3.6771428571428575}"
