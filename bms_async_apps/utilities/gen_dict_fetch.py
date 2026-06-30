# gen_dict_fetch.py  template msg["x"] assignment statements
import sqlite3

class GenDictCols:
    def __init__(self, dbname):
        self.db_path = dbname
        
    def get_cursor(self):
        self.cx = sqlite3.connect(self.db_path)
        self.cx.isolation_level = None
        cu = self.cx.cursor()
        return cu
    
    def get_column_headers(self, table_name):
        headers=[]
        cu = self.get_cursor()
        select_str = f" select * from {table_name}"
        data = cu.execute(select_str)
        for column in data.description:
            headers.append(column[0])
        return headers
    
    def create_dict_fetches(self, tablename):
        hdrs = self.get_column_headers(tablename)
        for h in hdrs:
            print(f"msg[\"{h}\"]")
            
    def get_schemas(self):
        records=[]
        cu=self.get_cursor()
        str_select = "select sql from sqlite_schema where type='table'"
        for row in cu.execute(str_select):
            records.append(row)
        print(f" schemas: {records}")
        return records
       
        
    