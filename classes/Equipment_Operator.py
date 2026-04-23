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
    att = ['id', 'equipment_id', 'operator_id', 'utilization_date', 'cost']

    def __init__(self, id, equipment_id, operator_id, utilization_date, cost):
        super().__init__()
        self.id = type(self).get_id(id)
        self.equipment_id = int(equipment_id)
        self.operator_id = int(operator_id)
        self.utilization_date = utilization_date
        self.cost = float(cost)
        
        type(self).obj[self.id] = self
        type(self).lst.append(self.id)

    def get_year(self):
        return self.utilization_date.split('/')[-1]

    def get_efficiency_score(self):
        if self.cost == 0:
            return "N/A"
        return round(1000 / self.cost, 2)

    def is_weekend_operation(self):
        day, month, year = map(int, self.utilization_date.split('/'))
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
        return [o.equipment_id for o in cls.obj.values() if o.operator_id == op_id]

    def __str__(self):
        return f"Log:{self.id}|Op:{self.operator_id}|Eq:{self.equipment_id}|Cost:{self.cost}"
    
