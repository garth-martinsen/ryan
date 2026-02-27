#file: create LUT table insert statements

from collections import OrderedDict


class SqlWorker:
    '''this class was created to populate the LUT for channel 0,1,2 for a project_id. The LUT will be later, updated during calibration.
     example: sw=SqlWorker();   sw.make_inserts('LUTS', 1, 0, 2.0, 0.095, 25, 46)  generates 112 insert statements for channel 0.
    def __init__(self):
        self.table = 'LUTS'
        
    def make_inserts(self, table, project_id, channel, vm0, vmstep, vin_min, vin_max):
        '''Creates statements that can be copy-pasted into sqlite CLI.
        vin0 and vinend are ten times vin_start and vin_end, vm0 is starting value of vm
        vmstep is the increment in vm for each vin '''
        cnt =0
        for v in range(vin_min,vin_max):
            vin = v/10
            vm= round((vm0 + cnt*vmstep),5)
            statement = f"insert into {table} values( NULL, {project_id}, {channel}, {vm}, {vin}); "
            print(statement)
            cnt +=1
         
    def read_csv_file(self, filename):
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
        return od
                
                
                
    