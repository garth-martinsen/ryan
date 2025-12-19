#file: lut_convert.py
from collections import OrderedDict
import json


class LutConvert:
    '''Need a way to take an OrderedDict[float: float] in the server and convert it to a form that will json.loads(),
Then reverse the process in the client to restore the original OrderedDict.
The solution to this problem is to convert the odict to a List[List[float,float]]. Then convert back using odict(list)'''
    
    def list_to_odict(self, jsonlist ):
        '''takes a List[list[float, float]] and returns an OrderedDict.'''
        lst_lists =json.loads(jsonlist)
        return OrderedDict(lst_lists)

    def odict_to_list(self, odict: OrderedDict):
        '''Generate a list, olst, of List[float:float] from odict'''
        olst = [[k,v] for k,v in odict.items()]
        return json.dumps(olst)
