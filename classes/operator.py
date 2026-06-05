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
        id = Operator.get_id(id)
        self._id = id
        self._title = title
        self._category = category
        
        if isinstance(birth_date, (datetime.date, datetime.datetime)):
            self._birth_date = birth_date.strftime("%d/%m/%Y")
        else:
            val_str = str(birth_date).strip()
            try:
                dt = datetime.datetime.strptime(val_str, "%Y-%m-%d")
                self._birth_date = dt.strftime("%d/%m/%Y")
            except ValueError:
                self._birth_date = val_str
        
        Operator.obj[id] = self
        if id not in Operator.lst: 
            Operator.lst.append(id)
    
    @property 
    def id(self): return self._id
    @id.setter 
    def id(self, id): self._id = id
    
    @property 
    def title(self): return self._title
    @title.setter 
    def title(self, title): self._title = title
    
    @property 
    def category(self): return self._category
    @category.setter 
    def category(self, category): self._category = category
    
    @property 
    def birth_date(self): 
        return self._birth_date
        
    @birth_date.setter 
    def birth_date(self, dob):
        if isinstance(dob, (datetime.date, datetime.datetime)):
            self._birth_date = dob.strftime("%d/%m/%Y")
        else:
            val_str = str(dob).strip()
            try:
                dt = datetime.datetime.strptime(val_str, "%Y-%m-%d")
                self._birth_date = dt.strftime("%d/%m/%Y")
            except ValueError:
                self._birth_date = val_str
                
    @property
    def age(self):
        try:
            # Converte temporariamente para calcular a idade com precisão
            dt_birth = datetime.datetime.strptime(self._birth_date, "%d/%m/%Y").date()
            hoje = datetime.date.today()
            idade = hoje.year - dt_birth.year
            if hoje.month < dt_birth.month or (hoje.month == dt_birth.month and hoje.day < dt_birth.day):
                idade -= 1
            return idade
        except Exception:
            return "N/A"