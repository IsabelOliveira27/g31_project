# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 13:56:42 2026

@author: isabel
"""
from classes.gclass import Gclass
import datetime

class Equipment_operator(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    att = ['_id', '_equipment_id', '_operator_id', '_utilization_date', '_cost']
    header = 'Equipment_Operator'
    des = ["ID", "Equipment_ID", "Operator_ID", "Utilization_date", "Cost"]

    def __init__(self, id, equipment_id, operator_id, utilization_date, cost):
        super().__init__()
        novo_id = Equipment_operator.get_id(id)
        self._id = novo_id
        self._equipment_id = int(equipment_id)
        self._operator_id = int(operator_id)
        self._cost = float(cost)
        
        if isinstance(utilization_date, (datetime.date, datetime.datetime)):
            self._utilization_date = utilization_date
        else:
            try:
                self._utilization_date = datetime.datetime.strptime(str(utilization_date).strip(), "%d/%m/%Y").date()
            except ValueError:
                self._utilization_date = datetime.datetime.strptime(str(utilization_date).strip(), "%d/%m/%Y").date()

        Equipment_operator.obj[novo_id] = self
        if novo_id not in Equipment_operator.lst: Equipment_operator.lst.append(novo_id)

    @property
    def id(self): 
        return self._id
    
    @id.setter
    def id(self, value): 
        self._id = value
        
    @property
    def operator_id(self): 
        return self._operator_id
    
    
    @operator_id.setter
    def operator_id(self, operator_id): 
        self._operator_id = int(operator_id)
        
    @property    
    def equipment_id(self): 
        return self._equipment_id
    
    @equipment_id.setter
    def equipment_id(self, equipment_id): 
        self._equipment_id = int(equipment_id)

    @property
    def utilization_date(self):
        return self._utilization_date.strftime('%d/%m/%Y')
    
    @utilization_date.setter
    def utilization_date(self, value):
        if isinstance(value, (datetime.date, datetime.datetime)):
            self._utilization_date = value
        else:
            try:
                self._utilization_date = datetime.datetime.strptime(str(value).strip(), "%d/%m/%Y").date()
            except ValueError:
                self._utilization_date = datetime.datetime.strptime(str(value).strip(), "%d/%m/%Y").date()

    @property
    def cost(self): return self._cost
    @cost.setter
    def cost(self, value): self._cost = float(value)

    @property
    def get_efficiency_score(self):
        if self._cost == 0: return "N/A"
        return round(1000 / self._cost, 2)

