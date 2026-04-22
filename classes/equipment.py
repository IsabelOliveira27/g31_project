#Class Equipment

from classes.gclass import Gclass
from datetime import datetime
class Equipment(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    
    # Attribute names list, identifier attribute must be the first one and callled 'id'
    att = ['_id','_name','_creation_date']
           
    # Class header title
    header = 'Equipments'
    
    # field description for use in, for example, input form
    des = ['Id','Name of the Equipment', 'Date of Creation']
    
    # Constructor: Called when an object is instantiated
    def __init__(self, id, name, creation_date):
        super().__init__()
        # Object attributes
        id = Equipment.get_id(id)
        self._id = id
        self._name = name
        self._creation_date = datetime.strptime(creation_date, '%d/%M/%Y')
        # Add the new object to the dictionary of objects
        Equipment.obj[id] = self
        # Add the id to the list of object ids
        Equipment.lst.append(id)
        
    # id property getter method
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, id):
        self._id = id
        
    # name property getter method
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name
        
    # creation_date property getter method
    @property
    def creation_date(self):
        return datetime.strftime(self._creation_date, '%d/%M/%Y')
    
    # creation_date property setter method
    @creation_date.setter
    def creation_date(self, new_date):
        self._creation_date = datetime.strptime(new_date, '%d/%M/%Y')
        return self._creation_date


    
e = Equipment(120, 'Bond', '14/02/2025')
print(e.name)
print(e.creation_date)
print(e.id)

