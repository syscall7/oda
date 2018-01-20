'''
Created on Jul 7, 2012

@author: Owner
'''

class InstructionType:
    normal = 0
    branch = 1
    call = 2
    undefined = 3
    data = 4

class callType:
    direct = 0
    indirect = 1    

class RefUnit(object):
    def __init__(self, vma):
        self.vma = vma



