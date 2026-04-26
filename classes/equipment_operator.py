# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 13:56:42 2026

@author: isabe
"""
from gclass import Gclass
import datetime



class Equipment_Operator(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    att = ['_id', '_equipment_id', '_operator_id', '_utilization_date', '_cost']
    header = 'Equipment_Operator'
    des = ["ID", "Equipment_ID", "Operator_ID", "Utilization_date", "Cost"]

    def __init__(self, id, equipment_id, operator_id, utilization_date, cost):
        super().__init__()
        self._id = type(self).get_id(id)
        self._equipment_id = int(equipment_id)
        self._operator_id = int(operator_id)
        self._utilization_date = utilization_date
        self._cost = float(cost)
        
        type(self).obj[self.id] = self
        type(self).lst.append(self.id)

    @property
    def id(self):
        return self._id

    @property
    def equipment_id(self):
        return self._equipment_id

    @property
    def operator_id(self):
        return self._operator_id

    @property
    def utilization_date(self):
        return datetime.datetime.strptime(self._utilization_date, "%d/%m/%Y").date()
        
    @property
    def cost(self):
        return self._cost
    
    @id.setter
    def id(self,id):
        self._id=id

    @equipment_id.setter
    def equipment_id(self,equipment_id):
        self._equipment_id = equipment_id

    @operator_id.setter
    def operator_id(self,operator_id):
        self._operator_id = operator_id

    @utilization_date.setter
    def utilization_date(self, utilization_date):
        self._utilization_date = utilization_date
        
    @cost.setter
    def cost(self,cost):
        self._cost = cost

    @property
    def get_year(self):
        return self._utilization_date.split('/')[-1]

    @property
    def get_efficiency_score(self):
        if self._cost == 0:
            return "N/A"
        return round(1000 / self.cost, 2) 

    @property
    def is_weekend_operation(self):
        day, month, year = map(int, self._utilization_date.split('/'))
        dt = datetime.date(year, month, day)
        return dt.weekday() >= 5

    @classmethod
    def get_total_spending(cls):
        return sum(float(o.cost) for o in cls.obj.values())

    @classmethod
    def filter_by_cost_range(cls, min_v, max_v):
        return [o.id for o in cls.obj.values() if min_v <= o.cost <= max_v]

    @classmethod
    def find_operator_usage(cls, op_id):
        return [o._equipment_id for o in cls.obj.values() if o._operator_id == op_id]

    def __str__(self):
        return f"Log:{self.id}|Op:{self._operator_id}|Eq:{self._equipment_id}|Cost:{self._cost}"
    

    
