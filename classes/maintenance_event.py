# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 14:40:22 2026

@author: Constança Figueiredo
"""
from classes.gclass import Gclass
import datetime

class Maintenance_event(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey =''

    att = ["_id", "_equipment_id", "_maintenance_type_id", "_maintenance_date", "_extra_info", "_maintenance_date_final"]
    header = "Maintenance_event"
    des = ["id", "equipment_id", "maintenance_type_id", "maintenance_date", "extra_info","maintenance_date_final"]

    def __init__(self, id, equipment_id, maintenance_type_id, maintenance_date, extra_info, maintenance_date_final):
        super().__init__()
        id = Maintenance_event.get_id(id)
        self._id = id
        self._equipment_id = int(equipment_id)
        self._maintenance_type_id = int(maintenance_type_id)
        self._extra_info = extra_info
        
        if isinstance(maintenance_date, (datetime.date, datetime.datetime)):
            self._maintenance_date = maintenance_date
        else:
            try:
                self._maintenance_date = datetime.datetime.strptime(str(maintenance_date).strip(), "%Y-%m-%d").date()
            except ValueError:
                self._maintenance_date = datetime.datetime.strptime(str(maintenance_date).strip(), "%d/%m/%Y").date()


        if isinstance(maintenance_date_final, (datetime.date, datetime.datetime)):
            self._maintenance_date_final = maintenance_date_final
        else:
            try:
                self._maintenance_date_final = datetime.datetime.strptime(str(maintenance_date_final).strip(), "%Y-%m-%d").date()
            except ValueError:
                self._maintenance_date_final = datetime.datetime.strptime(str(maintenance_date_final).strip(), "%d/%m/%Y").date()


        Maintenance_event.obj[id] = self
        if id not in Maintenance_event.lst: Maintenance_event.lst.append(id)

    @property
    def id(self): return self._id
    @id.setter
    def id(self, id): self._id = id
    
    @property
    def maintenance_type_id(self): return self._maintenance_type_id
    @maintenance_type_id.setter
    def maintenance_type_id(self, maintenance_type_id): self._maintenance_type_id = int(maintenance_type_id)
        
    @property
    def equipment_id(self): return self._equipment_id
    @equipment_id.setter
    def equipment_id(self, equipment_id): self._equipment_id = int(equipment_id)
    
    @property
    def maintenance_date(self):
        return self._maintenance_date
    @maintenance_date.setter
    def maintenance_date(self, maintenance_date):
        if isinstance(maintenance_date, (datetime.date, datetime.datetime)):
            self._maintenance_date = maintenance_date
        else:
            try:
                self._maintenance_date = datetime.datetime.strptime(str(maintenance_date).strip(), "%Y-%m-%d").date()
            except ValueError:
                self._maintenance_date = datetime.datetime.strptime(str(maintenance_date).strip(), "%d/%m/%Y").date()
    
    @property
    def maintenance_date_final(self):
        return self._maintenance_date_final
    
    
    @maintenance_date_final.setter
    def maintenance_date_final(self, maintenance_date_final):
        if isinstance(maintenance_date_final, (datetime.date, datetime.datetime)):
            self._maintenance_date_final = maintenance_date_final
        else:
            try:
                self._maintenance_date_final = datetime.datetime.strptime(str(maintenance_date_final).strip(), "%Y-%m-%d").date()
            except ValueError:
                self._maintenance_date_final = datetime.datetime.strptime(str(maintenance_date_final).strip(), "%d/%m/%Y").date()
    
    
    @property
    def extra_info(self): return self._extra_info
    @extra_info.setter
    def extra_info(self, extra_info): self._extra_info = extra_info