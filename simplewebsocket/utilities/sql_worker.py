#file: create LUT table insert statements

from collections import OrderedDict
import time
from worker_named_tuples import Config_fields , cfg1, Config_fields2,cfg2

FSR=4.096
STEPS=32768
LSB=FSR/STEPS
    
class SqlWorker:
    '''this class was created to populate the LUTs table for channel 0,1,2 for a project_id. The LUT can be later, updated during calibration.
     The three examples below will create 93  records in the luts table after you have emptied the LUTS table for that app_id 
     example: sw=SqlWorker();
     sw.make_inserts('LUTS', 1, 0,  30, 46)                  generates 16 insert statements for chan 0
     example: sw.make_inserts('LUTS', 1, 1, 60, 91)   generates 31 insert statements for chan 1
     example:sw.make_inserts('LUTS', 1,  2, 90, 136) generates 46 insert statements for chan 2
     Calibration will correct the vm values to close to the same as generated values. It should be noted that the keys in the luts never
     exceed the FSR of 4.095V
     Usage: measure your r1 and r2 on each circuit. Compute the fraction = r2/(r1+r2) and place it in the
     vm_k variables in the make_inserts(...) method. the vm_k values should approximbate 2/3, 1/3, 1/4'''
    
 
    def __init__(self):
        self.table = 'LUTS'
        self.luts= [OrderedDict(),OrderedDict(),OrderedDict()]
        self.vd_fract =  {0:0.688128140703518  , 1:0.313249211356467, 2: 0.248189762796504  }
        
    
    def _timestamp(self):
        """Returns local time as string, eg: YYYY-mm-DD HH:MM:SS"""
        dt = time.localtime()
        return f"{dt[0]}-{dt[1]}-{dt[2]}_{dt[3]}:{dt[4]}:{dt[5]}"  # YYYY-MM-DD  HH:mm:sec (dt[6] dow , dt[7] julian)
        
    def make_inserts(self, table, app_id, chan, vin_min, vin_max):
        '''Creates statements that can be copy-pasted into sqlite CLI to insert records into LUTS table.
        The app_id is 
        vin0 and vinend are ten times vin_start and vin_end, vm0 is starting value of vm . The scalars for each chan, vm_k,
        will be what the voltage divider provides: chan 0: vm=2/3*vin, chan1 : vm= 1/3 *vin, chan2: vm=1/4*vin. vm is rounded to 4 decimal places.'''
        od=OrderedDict()
        cnt =0
        vd_fract=self.vd_fract[chan]
        for v in range(vin_min,vin_max):
            vin = v/10
            vm= round(vin*vd_fract, 4)
            od[float(vm)]= float(vin)
            statement = f"insert into {table} values( NULL, {app_id}, {chan}, {vm}, {vin}); "
            print(statement)
            cnt +=1
            self.luts[chan]=od
        return od
        
    def read_csv_file(self, filename):
        '''Sqlite3 can output the results of a select statement to file. It is comma delimited so the filename can be XXX.csv.
           This method will read in the values '''
        od=OrderedDict()
        with open(filename, 'r') as file:
            headers = file.readline()
            print(headers)
            cnt=0
            records = 112
            while cnt < records:
                ln = file.readline()
                fields = ln.split(",")
                vm= float(fields[2])
                vin=float(fields[3])
                print(vm, "," , vin)
                od[vm]=vin
                cnt +=1
        self.luts[chan]=od
        return od

    def lookup_chan_vm(self,  chan, vm):
        '''Given any legitimate value for vm (measured voltage) in a channel, chan,  return the estimate of vb (battery voltage), using interpolation.
           First  if vm is == to a boundary returns lut.value, then if not out of bounds, interpolates vm to yield vb '''
        #  bracket vm with vlo and vhi
        lut=self.luts[chan]
        minkey=10
        maxkey=-10
        minval=15
        maxval=-15
        for k,v in lut.items():
            minkey=min(minkey, k)
            maxkey=max(maxkey,k)
            minval= min(minval,v)
            maxval=max(maxval,v)
        print( f"\t bounds for chan { chan} : {minkey} , {maxkey} which maps to: {minval} , {maxval}")
        # if vm is on a boundary , return lut(vm)
        if vm==minkey or vm==maxkey:
            return lut[vm]
        # if out of bounds return error statement
        elif vm < minkey or vm >= maxkey:
            return f" \t Error: vm is out of bounds. violates: {minkey} <=  vm: {vm}  < {maxkey}. "
        else:
            #  if inside boundaries, find keys that bracket vm
            print(f"\tvm is in range.: {minkey}  <=  {vm}  <  {maxkey} ... OK")
            vhi=-1
            vlo=10
            for k,v in lut.items():
                if vm < k:
                    vhi=k
                    break    # important! w/o break vhi will run all the way to highest vm in od.
                else:
                    vlo=k
            # then interpolate using vlo,vhi, vm
            print(f"\tvlo: {vlo} vm: {vm}  vhi: {vhi}")
            rvm = vhi - vlo
            fract=(vm-vlo)/rvm
            vbhi=lut[vhi]
            vblo=lut[vlo]
            vb = round(vblo + fract * (vbhi-vblo), 3)
            # print(f"interpolated value for {vm} is {vb}")
            return vb
     #TODO 1:Finish and test method create_cols_vals(...)  so a table with a new schema  can be loaded from the old table (.schema)

    def create_cols_vals(self, data, schema):
        '''Removes fields not in schema, Returns two lists with column names (cols) and values (vals) to facilitate inserts into db.'''
        cols=[]
        vals=[]
        for k,v in data._asdict().items():
            if k not in schema:
                print("exclude: ", k)
            else:
                cols.append(k)
                vals.append(v)
        return (cols, vals)
    
    


        
        
            
sw=SqlWorker()
#populates the luts
sw.make_inserts('LUTS', 1, 0,   30,   46)
sw.make_inserts('LUTS', 1, 1,   60,   91)
sw.make_inserts('LUTS', 1, 2,   90, 136)
print("For: sw.lookup_chan_vm(0,2.345):")
print("\t", sw.lookup_chan_vm(0,2.345))
print("For: sw.lookup_chan_vm(1,2.345):")
print("\t", sw.lookup_chan_vm(1,2.345))
print("For: sw.lookup_chan_vm(2,2.345):")
print("\t", sw.lookup_chan_vm(2,2.345))



                
    