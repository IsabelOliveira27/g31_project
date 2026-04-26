print("-----Teste Classe Equipment-----")
print("\n")

e2=Equipment(12,"Maria", "24/04/2026")
print(e2)
e2.id = 14
e2.name = "João"
e2.creation_date = "26/04/2026"
print("\n")
print("Alteração dos atributos")
print(e2)
print("\n")




print("-----Teste Classe Equipment_Operator-----")
print("\n")

e1=Equipment_Operator(12, 144, 20, "27/03/2007", 30)
print(e1)
e1.id= 18
e1.equipment_id = 200
e1.operator_id = 30
e1.utilization_date = "12/11/2017"
e1.cost = 70
print("\n")
print("Alteração dos atributos")

print(e1)
print(e1.get_year)
print(e1.is_weekend_operation)
print(e1.get_efficiency_score)
print("\n")



print("-----Teste Maintenance Type-----")
print("\n")
m=Maintenance_Type(20, 40)
print(m)
m.id=33
m.equipment_id = 45
print("\n")
print("Alteração dos atributos")
print(m)
print("\n")


print("-----Teste Operator-----")
print("\n")
o=Operator(19, "Manager", "Junior", "01/01/2000")
print(o)    
o.id=20
o.title= "Manager Sr"
o.category="Senior"
o.birth_date="02/02/2002"
print("\n")
print("Alteração dos atributos")
print(o)
print(o.age)
print("\n")



print("-----Teste Maintenance Event-----")
print("\n")
m3=Maintenance_event(12, 14, 29, "04/09/2989", "preventivo")
print(m3)
m3.Maintenance_Date= "04/08/2029"
m3.id=19
m3.equipment_id=6
m3.maintenance_type_id=20
m3.extra_info="manutenção"
print("\n")
print("Alteração dos atributos")
print(m3)