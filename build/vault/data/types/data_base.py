from abc import ABCMeta, abstractmethod
from data_base import BaseData

class BaseData(metaclass=ABCMeta):
    rights = {}
    def __init__(self):
        rights = {'admin' : { 'read', 'write', 'append', 'delegate'}}
        

    @abstractmethod    
    def finalize(self): pass


    def authenticate(self, user_id, right):
        if user_id in self.rights:
            if right in self.rights[user_id].rights:
                return true

        return False
    