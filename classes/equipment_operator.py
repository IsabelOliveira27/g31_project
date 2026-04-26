# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 13:56:42 2026

@author: isabel
"""
from classes.gclass import Gclass
from datetime import datetime


class Equipment_Operator(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    att = ['_id', '_equipment_id', '_operator_id', '_utilization_date', '_cost']
    header = 'Equipment_Operator'
    des = ["ID", "Equipment_ID", "Operator_ID", "Utilization_date", "Cost"]

    def __init__(self, id, equipment_id, operator_id, utilization_date, cost):
        super().__init__()
        
        novo_id = Equipment_Operator.get_id(id)
        self._id = novo_id
        self._equipment_id = int(equipment_id)
        self._operator_id = int(operator_id)
        self._utilization_date = utilization_date 
        self._cost = float(cost)
        

        Equipment_Operator.obj[novo_id] = self
        Equipment_Operator.lst.append(novo_id)

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
        self._operator_id = operator_id
        
    @property    
    def equipment_id(self):
        return self._equipment_id
    
    @equipment_id.setter
    def equipment_id(self, equipment_id):
        self._equipment_id = equipment_id

    @property
    def utilization_date(self):
        if isinstance(self._utilization_date, str):
            return datetime.strptime(self._utilization_date, "%d/%m/%Y")
        return self._utilization_date

    @utilization_date.setter
    def utilization_date(self, value):
        self._utilization_date = value

    @property
    def cost(self):
        return self._cost

    @cost.setter
    def cost(self, value):
        self._cost = float(value)

    @property
    def get_year(self):
        return str(self._utilization_date).split('/')[-1]

    @property
    def is_weekend_operation(self):
        dt = self.utilization_date
        return dt.weekday() >= 5

    @property
    def get_efficiency_score(self):
        if self._cost == 0:
            return "N/A"
        return round(1000 / self._cost, 2)

    def __str__(self):
        return f"Log:{self._id}|Op:{self._operator_id}|Eq:{self._equipment_id}|Date:{self._utilization_date}|Cost:{self._cost}"
    
