#file: create LUT table insert statements

from collections import OrderedDict


class SqlWorker:
    '''this class was created to populate the LUT for channel 0,1,2 for a project_id. The LUT can be later, updated during calibration.
     The three examples below will create 100 records in the luts table, all starting with vm = 2.0 V and ending with vm < 4.095V:
     example: sw=SqlWorker();   sw.make_inserts('LUTS', 1, 0, 2.0, 0.095, 30, 46)  generates 16 insert statements for channel 0
     example: sw.make_inserts('LUTS', 1, 1,2.0, 0.0667, 60, 91) generates 31 statements
     example:sw.make_inserts('LUTS', 1, 2,2.0,  0.04255, 90, 136) generates 46 statements
     Calibration will correct the vm values to close to the same as generated values. It should be noted that the keys in the luts never
     exceed the FSR of 4.095V '''
    
    def __init__(self):
        self.table = 'LUTS'
        self.luts= [OrderedDict(),OrderedDict(),OrderedDict()]
        
    def make_inserts(self, table, app_id, chan, vm0, vin_min, vin_max):
        '''Creates statements that can be copy-pasted into sqlite CLI to insert records into LUTS table.
        The app_id is 
        vin0 and vinend are ten times vin_start and vin_end, vm0 is starting value of vm . The scalars for each chan, vm_k,
        will be what the voltage divider provides: chan 0: vm=2/3*vin, chan1 : vm= 1/3 *vin, chan2: vm=1/4*vin. vm is rounded to 4 decimal places.'''
        od=OrderedDict()
        cnt =0
        vm_k = 0
        if chan == 0 :
            vm_k=2/3
        elif chan == 1:
            vm_k = 1/3
        elif chan == 2:
            vm_k= 1/4
            
        for v in range(vin_min,vin_max):
            vin = v/10
            vm= round(vin*vm_k, 4)
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
        '''Given any legitimate value for vm (measured voltage) in a channel, chan,  return the estimate of vb (battery voltage), using interpolation'''
        #  bracket vm with vlo and vhi
        lut=self.luts[chan]
        minkey=10
        maxkey=-10
        for k in lut.keys():
            minkey=min(minkey, k)
            maxkey=max(maxkey,k)
        print( "bounds: " ,minkey, maxkey)
        if vm < minkey or vm >= maxkey:
            print( f" vm is out of bounds. violates: {minkey} <=  vm: {vm}  < {maxkey}. ")
        else:
            print(f"Vm is in range.: {minkey}  <=  {vm}  <=  {maxkey}")
            vhi=-1
            vlo=10
            for k,v in lut.items():
                if vm < k:
                    vhi=k
                    break    # important! w/o break vhi will run all the way to highest vm in od.
                else:
                    vlo=k

            # interpolate using vlo,vhi, vm
            print(f"vlo: {vlo} vm: {vm}  vhi: {vhi}")
            rvm = vhi - vlo
            fract=(vm-vlo)/rvm
            vbhi=lut[vhi]
            vblo=lut[vlo]
            vb = round(vblo + fract * (vbhi-vblo), 3)
            # print(f"interpolated value for {vm} is {vb}")
            return vb
            
                
                
    