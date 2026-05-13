#file : server_computes.py

import math

samps = [22657, 22654, 22651, 22653, 22655, 22657, 22651, 22657, 22651, 22655, 22657, 22653, 22656, 22658, 22656, 22658, 22657, 22655, 22653, 22655, 22655, 22655, 22655, 22656, 22651, 22658, 22656, 22658, 22658, 22653, 22652, 22658, 22658, 22653, 22655, 22657, 22654, 22651, 22653, 22655, 22657, 22651, 22657, 22651, 22655, 22657, 22653, 22656, 22658, 22656, 22658, 22657, 22657, 22654, 22651, 22653, 22655, 22657, 22651, 22657, 22651, 22655, 22657, 22653]
lsb=125e-6
vd_fracts=[0.688128140703518, 0.313249211356467, 0.248189762796504]

class ServerComps:
    def __init__(self):
        pass
        
    def avg(self, alst):
        return sum(alst)/len(alst)
    
    def std_dev(self, m, samples):
        vrs= [(x-m)*(x-m) for x in samples]
        vrs_m= self.avg(vrs)
        sd=math.sqrt(vrs_m)
        return sd

    def compute(self, samples, lsb, chan, vin):
        '''Emulates the server computing to complete the BMS tuple...'''
        m=self.avg(samples)
        sd = self.std_dev(m, samples)   # sd of a2d samples
        # keep will be used for stats after discarding outliers...
        keep = [x for x in samples if abs(x-m) <  3*sd]
        m=self.avg(keep)
        sd = self.std_dev(m,keep)
        vm_m  = m* lsb                           
        vm_sd =  sd* lsb
        vb = vm_m/vd_fracts[chan]
        err = vin - vb
        num = len(keep)
        atpl = (m, vm_m, vm_sd, vb, vin, err, num)
        print("atpl: ", atpl)
        return atpl
        
        
        