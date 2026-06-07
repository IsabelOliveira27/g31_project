#Class Equipment

from classes.gclass import Gclass
import datetime 
class Equipment(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    
    # Attribute names list, identifier attribute must be the first one and callled 'id'
    att = ['_id','_name','_creation_date', '_type']
           
    # Class header title
    header = 'Equipments'
    
    # field description for use in, for example, input form
    des = ['Id','Name of the Equipment', 'Date of Creation', 'Type of Equipment']
    
    # Constructor: Called when an object is instantiated
    def __init__(self, id, name, creation_date, tipo):
        super().__init__()
        # Object attributes
        id = Equipment.get_id(id)
        self._id = id
        self._name = name
        self._creation_date = datetime.datetime.strptime(creation_date, '%d/%m/%Y').date()
        self._tipo = tipo 
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
        return self._creation_date.strftime('%d/%m/%Y')

    # creation_date property setter method
    @creation_date.setter
    def creation_date(self, new_date):
        self._creation_date = datetime.datetime.strptime(new_date, '%d/%m/%Y').date()

    @property
    def tipo(self):
        return self._type

    @tipo.setter
    def tipo(self,  new_type):
        self._type = new_type 
        return self._type
        
    def __str__(self):
        return f"Log:{self._id} | Name of the Equipment:{self.name}|Date of creation:{self.creation_date}"

    @classmethod
    def marca_mais_usada(cls):
        lst_brand = {}
        for equip in Equipment.obj.values():
            marca = equip.name
            if marca in lst_brand:
                lst_brand[marca] += 1  
            else:
                lst_brand[marca] = 1   
        moda = max(lst_brand, key=lst_brand.get)
        return f"A marca mais utilizada para os equipamentos da fábrica é {moda}."
                
    @classmethod 
    def equipamento_mais_antigo(cls):
        lista_valores = list(cls.obj.values())
        eq_inicial = lista_valores[0]

        for equi in Equipment.obj.values():
            if equi._creation_date < eq_inicial._creation_date:
                eq_inicial=equi 
        return f"O equipamento mais antigo é ID:{eq_inicial.id} - {eq_inicial.name}, comprado a {eq_inicial.creation_date}"

    @classmethod 
    def  dia_mais_equipamentos(cls):
        lst_dates = {}
        for equip in Equipment.obj.values():
            data = equip.creation_date
            if data in lst_dates:
                lst_dates[data] += 1  
            else:
                lst_dates[data] = 1   
        dia_D = max(lst_dates, key=lst_dates.get)
        return f"Adquiriu-se mais equipamentos no dia {dia_D}."
