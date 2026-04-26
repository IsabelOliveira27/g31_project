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
