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
    att = ['_maintenance_type_id','_equipment_id']
    header = 'Maintenance Types'
    des = ['MaintTypeId','EquipId']
    
    def __init__(self, maintenance_type_id, equipment_id):
        super().__init__()
        
        maintenance_type_id = Maintenance_Type.get_id(maintenance_type_id)
        self._maintenance_type_id = maintenance_type_id
        self._equipment_id = equipment_id
        
        Maintenance_Type.obj[maintenance_type_id] = self
        Maintenance_Type.lst.append(maintenance_type_id)
    
    @property
    def maintenance_type_id(self):
        return self._maintenance_type_id
    @maintenance_type_id.setter
    def maintenance_type_id(self, maintenance_type_id):
        self._maintenance_type_id = maintenance_type_id
    
    @property
    def equipment_id(self):
        return self._equipment_id
    @equipment_id.setter
    def equipment_id(self, equipment_id):
        self._equipment_id = equipment_id
