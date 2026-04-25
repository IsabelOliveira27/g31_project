# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 14:40:22 2026

@author: Constança Figueiredo
"""

import datetime

class Maintenance_event (Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey =''

att = ["id", "_date_main", "_extra_info"]

header = "Maintenance_event"

des = ["id", "_date_main", "_extra_info"]

def _init_(self,id, maintenance_type_id, equipment_id, maintenance_date, extra_info):
    super()._init__()

    id = Maintenance_event.get_id(id)
    self._id = id
    self._maintenance_type_id = maintenance_type_id
    self._equipment_id = equipment_id
    self._extra_info = extra_info
    self._maintenance_date = datetime.strptime(maintenance_date, "%d/%m/Y"). date()

    Maintenance_event.obj[id] = self

    Maintenance_event.lst.append(id)

@property
def id(self):
    return self.id

@id.setter
def id(self,id):
    self._id = id

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
    self._equipment_id= equipment_id


@property
def maintenance_date(self):
    return self._maintenance_date

@maintenance_date. setter
def maintenance_date(self, maintenance_date):
    self._maintenance_date = maintenance_date

@property
def extra_info(self):
    return self._extra_info

@extra_info.setter
def extra_info(self, extra_info) :
    self._extra_info = extra_info
