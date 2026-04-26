# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 14:39:58 2026

@author: isabe
"""

from classes.gclass import Gclass

import datetime

class Operator(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ""
    
    att = ["_id", "_title", "_category", "_birth_date"]
    
    header = "Operators"
    
    des = ["Operator ID", "Title", "Category", "Date of birth"]
    
    def __init__(self, id, title, category, birth_date):
        super().__init__()
        # Object attributes
        id = Operator.get_id(id)
        self._id = id
        self._title = title
        self._category = category
        self._birth_date = datetime.datetime.strptime(birth_date, "%d/%m/%Y").date()
        
        Operator.obj[id] = self
        
        Operator.lst.append(id)
    
    @property 
    def id(self):
        return self._id
    
    @id.setter 
    def id(self, id):
        self._id = id
    
    
    @property 
    def title(self):
        return self._title
    
    @title.setter 
    def title(self, title):
        self._title = title
    
    
    @property 
    def category(self):
        return self._category
    
    @category.setter 
    def category(self, category):
        self._category = category
    
    
    @property 
    def birth_date(self):
        return self._birth_date
    
    @birth_date.setter 
    def birth_date(self, dob):
        if isinstance(dob, str):
            self._birth_date = datetime.datetime.strptime(dob, "%d/%m/%Y").date()
        else:
            self._birth_date = dob
    
    
    @property
    def age(self):
        hoje = datetime.date.today()
        idade = hoje.year - self._birth_date.year
        if hoje.month < self._birth_date.month or (hoje.month == self._birth_date.month and hoje.day < self._birth_date.day):
            idade -= 1
        return idade
