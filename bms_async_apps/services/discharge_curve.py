# file: discharge_curve.py

from collections import OrderedDict

'''This data is for one LiIon Cell. It must be studied further to apply it to 3 cells in series.'''
discharge_curve = OrderedDict({})
discharge_curve[0]=4.2
discharge_curve[100]= 4.1
discharge_curve[200]= 4.0
discharge_curve[600]= 3.9
discharge_curve[800]= 3.8
discharge_curve[1300]= 3.7
discharge_curve[1850 ]= 3.6
discharge_curve[1920]= 3.5
discharge_curve[1980 ]=3.4 
discharge_curve[1990]=3.3 
discharge_curve[2000 ]= 3.2

class Interpolator:
'''Interpolates for Voltage in a partially depleted LiIon Cell that fall between keys in discharge curve... '''
    def __init__(self):
        self.dc=discharge_curve

    def interpolate(self, amp_hrs):
        for a,v in self.dc.items():
            if a >amp_hrs:
              ul=a
            else:
              bl = a
        hv = self.dc[ul]
        lv = self.dc[bl]
        vr = hv-lv
        fr = (amp_hrs - bl)/ (ul-bl)
        vb = lv + fr * vr
        return vb
             
