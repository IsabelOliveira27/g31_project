# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 14:40:49 2026

@author: isabe
"""

from classes.gclass import Gclass
class Maintenance_Type(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    att = ['_id','_equipment_id']
    header = 'Maintenance Types'
    des = ['MaintTypeId','EquipId']
    
    def __init__(self, id, equipment_id):
        super().__init__()
        
        id = Maintenance_Type.get_id(id)
        self._id = id
        self._equipment_id = equipment_id
        
        Maintenance_Type.obj[id] = self
        Maintenance_Type.lst.append(id)
    
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, id):
        self._id = id
    
    @property
    def equipment_id(self):
        return self._equipment_id
    @equipment_id.setter
    def equipment_id(self, equipment_id):
        self._equipment_id = equipment_id
        
    @classmethod
    def count_by_equipment(cls, equipment_id=None):
        counts = {}
        for k in cls.lst:
            eq_id = cls.obj[k].equipment_id
            counts[eq_id] = counts.get(eq_id, 0) + 1
        
        if equipment_id is not None:
            return counts.get(equipment_id, 0)
        return counts

    @classmethod
    def exists(cls, id):
        return id in cls.obj

    @classmethod
    def remove(cls, id):
        if not cls.exists(id):
            raise KeyError(f"Maintenance_Type with id '{id}' doesnt exist.")
        
        del cls.obj[id]
        cls.lst.remove(id)
