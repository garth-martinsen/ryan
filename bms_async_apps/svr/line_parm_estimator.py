file: svr/line_parm_estimator.py
from .lpe_cfg import luts

class LineParmEstimator:
    def __init__(self):
        self.points=[[],[],[]]
        self.slopes=[[],[],[]]
        self.intercepts=[[],[],[]]

    def compute_line_parms(self):
        for chan in range(3):
            self.compute_line_parms_for_chan(chan, luts[chan] )
            
    def compute_line_parms_for_chan(self, chan, points):
        ''' 
        points is a list of pairs (vm, vin) for channel, chan
        equation of line:  y = m*x + b   where b is y-intercept amd m is slope.
        m = n*( sum(x*y) -sum(x)*sum(y)) / n*sum(x**2)- (sum(x))**2
        b = (sum(yy) - m * sum(xx) / n*sum(x*x) - (sum(xx)**2)   #   
        ''' 
        self.points[chan] = points
        xx = [(x[0]) for x in points]         # list of x values
        yy = [(x[1]) for x in points]         # list of y values 
        x2x = [(x*x) for x in xx]             # list of x*x or x**2 values
        xy = [(x[0]*x[1]) for x in points]    # list of x*y values
        n=len(points)
        sx=sum(xx)
        sy=sum(yy)
        sxy =sum(xy)
        sx2 = sum(x2x)
   
        m = (n*sxy-sx*sy) / (n*sx2 - sx * sx) 
    
        b = (sy - m * sx)/n
        # save slope and intercept to self for later use but return chan, m, b for eye candy.
        self.slopes[chan] = m
        self.intercepts[chan] = b
        return (chan, m, b)

    def limits(self):
        '''Shows min (vm, vin) and max (vm, vin). for each chan. '''
        for chan in range(3):
            p=self.points[chan]
            print("chan: ", chan, p[0], p[-1] )

    def estimate_vb(self, chan, vm):
        '''Use the self.slopes[chan] and self.intercepts[chan] to compute vb. If vm is outside of limits, raises ValueError '''
        min_limit = self.points[chan][0][0]
        max_limit = self.points[chan][-1][0]
        if not min_limit <= vm <= max_limit:
            err = f"vm {vm} is out of bounds: {min_limit}, {max_limit} "
            raise ValueError(err)
        else:
            return vm * self.slopes[chan] + self.intercepts[chan]

