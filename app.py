from flask import Flask, render_template, request, session, redirect, url_for
from datafile import filename
import os

from classes.operator import Operator
from classes.equipment import Equipment
from classes.maintenance_event import Maintenance_event
from classes.maintenance_type import Maintenance_Type
from classes.equipment_operator import Equipment_Operator

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

db_path = os.path.join(filename, 'equipment_management.db') if not filename.endswith('/') else filename + 'equipment_management.db'

# Carregar dados da Base de Dados
Operator.read(db_path)
Equipment.read(db_path)
Maintenance_event.read(db_path)
Maintenance_Type.read(db_path)
Equipment_Operator.read(db_path)

prev_option = ""

def validar_foreign_keys(eq_id=None, op_id=None, type_id=None):
    """Verifica se os IDs existem na memória do sistema e se são superiores a 0."""
    try:
        if eq_id is not None:
            if int(eq_id) <= 0 or int(eq_id) not in Equipment.obj:
                return False
        if op_id is not None:
            if int(op_id) <= 0 or int(op_id) not in Operator.obj:
                return False
        if type_id is not None:
            if int(type_id) <= 0 or int(type_id) not in Maintenance_Type.obj:
                return False
        return True
    except (ValueError, TypeError):
        return False

def generic_crud(cls, request, form_fields, strobj_format):
    global prev_option
    butshow, butedit = "", "disabled" 
    option = request.args.get("option")
    id_att = cls.att[0]
    
    # --- MÓDULO DE PESQUISA VIA GCLASS ORIGINAL ---
    search_val = request.args.get("search_val")
    search_att = request.args.get("search_att")
    
    if option == "search" and search_val and search_att:
        real_att = next((a for a in cls.att if a == search_att or a[1:] == search_att), cls.att[1])
        ids_encontrados = cls.getlines(real_att, search_val)
        if not ids_encontrados and str(search_val).isdigit():
            ids_encontrados = cls.getlines(real_att, int(search_val))
            
        if ids_encontrados:
            cls.set_filter({real_att: [search_val if not str(search_val).isdigit() else int(search_val)]})
        else:
            cls.lst = []
            cls.pos = 0
        option = None 
    elif option == "clear_search":
        cls.set_filter({})
        option = None

    if option == "edit":
        butshow, butedit = "disabled", ""
    elif option == "delete":
        obj = cls.current()
        if obj:
            cls.remove(getattr(obj, id_att))
            if not cls.previous(): cls.first()
    elif option == "insert":
        butshow, butedit = "disabled", ""
    elif prev_option == 'insert' and option == 'save':
        next_id = cls.get_id(0)
        strobj = strobj_format(next_id, request.form)
        
        # Intercetar validação de chaves estrangeiras com base na classe ativa
        partes = strobj.split(';')
        if cls == Equipment_Operator and not validar_foreign_keys(eq_id=partes[1], op_id=partes[2]):
            return butshow, butedit, cls.current(), "insert"
        elif cls == Maintenance_event and not validar_foreign_keys(eq_id=partes[1], type_id=partes[2]):
            return butshow, butedit, cls.current(), "insert"
        elif cls == Maintenance_Type and not validar_foreign_keys(eq_id=partes[1]):
            return butshow, butedit, cls.current(), "insert"

        obj = cls.from_string(strobj)
        cls.obj[next_id] = obj
        if next_id not in cls.lst:
            cls.lst.append(next_id)
        cls.insert(next_id)
        cls.last()
    elif prev_option == 'edit' and option == 'save':
        obj = cls.current()
        if obj:
            # Validação na Edição
            if cls == Equipment_Operator and not validar_foreign_keys(eq_id=request.form.get(form_fields[0]), op_id=request.form.get(form_fields[1])):
                return "disabled", "", obj, "edit"
            elif cls == Maintenance_event and not validar_foreign_keys(eq_id=request.form.get(form_fields[0]), type_id=request.form.get(form_fields[1])):
                return "disabled", "", obj, "edit"
            elif cls == Maintenance_Type and not validar_foreign_keys(eq_id=request.form.get(form_fields[0])):
                return "disabled", "", obj, "edit"

            for field, att_name in zip(form_fields, cls.att[1:]):
                setattr(obj, att_name, request.form[field])
            cls.update(getattr(obj, id_att))
    elif option in ["first", "previous", "next", "last"]:
        getattr(cls, "nextrec" if option == "next" else option)()
    elif option == "cancel":
        butshow, butedit = "", "disabled"
        option = None

    if option in ["save", "delete", "cancel"]:
        prev_option = ""
    else:
        prev_option = option if option in ["insert", "edit"] else prev_option
        
    return butshow, butedit, cls.current(), option


from flask import request 

@app.route("/")
def dashboard():
    filtro_ano = request.args.get("ano", "Todos")
    filtro_mes = request.args.get("mes", "Todos")

    anos_disponiveis = ["2024", "2025", "2026"]
    meses_disponiveis = [
        {"num": "01", "nome": "Jan"}, {"num": "02", "nome": "Fev"},
        {"num": "03", "nome": "Mar"}, {"num": "04", "nome": "Abr"},
        {"num": "05", "nome": "Mai"}, {"num": "06", "nome": "Jun"},
        {"num": "07", "nome": "Jul"}, {"num": "08", "nome": "Ago"},
        {"num": "09", "nome": "Set"}, {"num": "10", "nome": "Out"},
        {"num": "11", "nome": "Nov"}, {"num": "12", "nome": "Dez"}
    ]

    custo_total_periodo = 0.0
    cronograma_dados = {}
    manut_equip = {}
    util_op = {}
    eficiencia_por_equip = {}

    for c in Equipment_Operator.lst:
        if c in Equipment_Operator.obj:
            uo = Equipment_Operator.obj[c]
            data_str = str(getattr(uo, 'utilization_date', '2026-05-01')) 
            
            partes = data_str.split("-")
            ano = partes[0] if len(partes) > 0 else "2026"
            mes = partes[1] if len(partes) > 1 else "05"

            if (filtro_ano != "Todos" and ano != filtro_ano): continue
            if (filtro_mes != "Todos" and mes != filtro_mes): continue

            custo = float(uo.cost) if getattr(uo, 'cost', None) else 0.0
            custo_total_periodo += custo

            chave_tempo = f"{ano}-{mes}" if filtro_ano == "Todos" else f"Dia {partes[2]}" if len(partes) > 2 else data_str
            cronograma_dados[chave_tempo] = cronograma_dados.get(chave_tempo, 0.0) + custo

            op_id = uo.operator_id
            op_name = Operator.obj[key]._title if (key := int(op_id)) in Operator.obj else f"OP #{op_id}"
            util_op[op_name] = util_op.get(op_name, 0) + 1

            eq_id = uo.equipment_id
            eq_name = Equipment.obj[key]._name if (key := int(eq_id)) in Equipment.obj else f"EQ #{eq_id}"
            ef = float(uo.get_efficiency_score) if hasattr(uo, 'get_efficiency_score') else 75.0
            if eq_name not in eficiencia_por_equip: eficiencia_por_equip[eq_name] = []
            eficiencia_por_equip[eq_name].append(ef)

    for c in Maintenance_event.lst:
        if c in Maintenance_event.obj:
            m = Maintenance_event.obj[c]
            eq_id = m.equipment_id
            eq_name = Equipment.obj[key]._name if (key := int(eq_id)) in Equipment.obj else f"EQ #{eq_id}"
            manut_equip[eq_name] = manut_equip.get(eq_name, 0) + 1


    total_avarias = sum(manut_equip.values()) or 1
    total_trabalhos = sum(util_op.values()) or 1


    g2_labels = list(manut_equip.keys())[:5] if manut_equip else ["Sem Registos"]
    g2_percentagens = [(v / total_avarias) * 100 for v in manut_equip.values()][:5] if manut_equip else [0]
    g2_absolutos = [f"{v} avarias" for v in manut_equip.values()][:5] if manut_equip else ["0"]


    g3_labels = list(util_op.keys())[:5] if util_op else ["Sem Registos"]
    g3_percentagens = [(v / total_trabalhos) * 100 for v in util_op.values()][:5] if util_op else [0]
    g3_absolutos = [f"{v} ordens" for v in util_op.values()][:5] if util_op else ["0"]

    g1_eixo_x = sorted(list(cronograma_dados.keys())) if cronograma_dados else ["Sem Dados"]
    g1_eixo_y = [cronograma_dados[k] for k in g1_eixo_x] if cronograma_dados else [0]


    g_azul_labels = list(eficiencia_por_equip.keys())[:5] if eficiencia_por_equip else ["Sem Dados"]
    g_azul_valores = [sum(l)/len(l) for l in eficiencia_por_equip.values()][:5] if eficiencia_por_equip else [0]

    return render_template(
        "dashboard.html",
        anos_disponiveis=anos_disponiveis,
        meses_disponiveis=meses_disponiveis,
        filtro_ano=filtro_ano,
        filtro_mes=filtro_mes,
        custo_total_periodo=custo_total_periodo,
        g1_x=g1_eixo_x, g1_y=g1_eixo_y,
        g2_labels=g2_labels, g2_y=g2_percentagens, g2_txt=g2_absolutos,
        g3_labels=g3_labels, g3_y=g3_percentagens, g3_txt=g3_absolutos,
        g_azul_labels=g_azul_labels, g_azul_valores=g_azul_valores
    )


@app.route("/operators", methods=["POST", "GET"])
def operators():
    fields = ["title", "category", "birth_date"]
    fmt = lambda next_id, f: f"{next_id};{f['title']};{f['category']};{f['birth_date']}"
    
    option = request.args.get("option")
    if option == "current":
        target_id = request.args.get("id")
        if target_id: Operator.current(int(target_id))

    butshow, butedit, obj, opt = generic_crud(Operator, request, fields, fmt)
    todos_registos = []
    for code in sorted(list(set(Operator.lst))):
        if code in Operator.obj:
            o = Operator.obj[code]
            todos_registos.append({
                "id": o.id, 
                "title": o.title, 
                "category": o.category, 
                "age": o.age
            })

    if opt == 'insert' or option == 'insert':
        return render_template("operators.html", butshow=butshow, butedit=butedit, id=Operator.get_id(0), title="", category="", birth_date="", todos_registos=todos_registos)
    
    b_date = getattr(obj, Operator.att[3]) if obj else ""
    
    return render_template("operators.html", butshow=butshow, butedit=butedit, 
                           id=getattr(obj, Operator.att[0]) if obj else Operator.get_id(0), 
                           title=getattr(obj, Operator.att[1]) if obj else "", 
                           category=getattr(obj, Operator.att[2]) if obj else "", 
                           birth_date=b_date, todos_registos=todos_registos)

# 2.equipamentos 
@app.route("/equipments", methods=["POST", "GET"])
def equipments():
    fields = ["name", "creation_date"]
    fmt = lambda next_id, f: f"{next_id};{f['name']};{f['creation_date']}"
    
    option = request.args.get("option")
    if option == "current":
        target_id = request.args.get("id")
        if target_id: Equipment.current(int(target_id))

    butshow, butedit, obj, opt = generic_crud(Equipment, request, fields, fmt)
    
    todos_registos = [Equipment.obj[code] for code in sorted(list(set(Equipment.lst))) if code in Equipment.obj]

    if opt == 'insert' or option == 'insert':
        return render_template("equipments.html", butshow=butshow, butedit=butedit, id=Equipment.get_id(0), name="", creation_date="", todos_registos=todos_registos)
    
    return render_template("equipments.html", butshow=butshow, butedit=butedit, 
                           id=getattr(obj, Equipment.att[0]) if obj else Equipment.get_id(0), 
                           name=getattr(obj, Equipment.att[1]) if obj else "", 
                           creation_date=getattr(obj, Equipment.att[2]) if obj else "", 
                           todos_registos=todos_registos)
# 3.utilizações
@app.route("/utilization", methods=["POST", "GET"])
def utilization():
    fields = ["equipment_id", "operator_id", "utilization_date", "cost"]
    fmt = lambda next_id, f: f"{next_id};{f['equipment_id']};{f['operator_id']};{f['utilization_date']};{f['cost']}"
    
    option = request.args.get("option")
    if option == "current":
        target_id = request.args.get("id")
        if target_id: Equipment_Operator.current(int(target_id))

    butshow, butedit, obj, opt = generic_crud(Equipment_Operator, request, fields, fmt)
    
    todos_registos = []
    for code in sorted(list(set(Equipment_Operator.lst))):
        if code in Equipment_Operator.obj:
            uo = Equipment_Operator.obj[code]
            todos_registos.append({"id": uo.id, "eq_id": uo.equipment_id, "op_id": uo.operator_id, "cost": uo.cost, "efficiency": uo.get_efficiency_score})

    if opt == 'insert' or option == 'insert':
        return render_template("utilization.html", butshow=butshow, butedit=butedit, id=Equipment_Operator.get_id(0), equipment_id="", operator_id="", utilization_date="", cost="", todos_registos=todos_registos)
    
    u_date = getattr(obj, Equipment_Operator.att[3]) if obj else ""
    if hasattr(u_date, "strftime"): u_date = u_date.strftime("%d/%m/%Y")

    return render_template("utilization.html", butshow=butshow, butedit=butedit, 
                           id=getattr(obj, Equipment_Operator.att[0]) if obj else Equipment_Operator.get_id(0), 
                           equipment_id=getattr(obj, Equipment_Operator.att[1]) if obj else "", 
                           operator_id=getattr(obj, Equipment_Operator.att[2]) if obj else "", 
                           utilization_date=u_date, 
                           cost=getattr(obj, Equipment_Operator.att[4]) if obj else "", todos_registos=todos_registos)

# 4. manutenções
@app.route("/maintenance", methods=["POST", "GET"])
def maintenance():
    fields = ["equipment_id", "maintenance_type_id", "maintenance_date", "extra_info"]
    fmt = lambda next_id, f: f"{next_id};{f['equipment_id']};{f['maintenance_type_id']};{f['maintenance_date']};{f['extra_info']}"
    
    option = request.args.get("option")
    if option == "current":
        target_id = request.args.get("id")
        if target_id: Maintenance_event.current(int(target_id))

    butshow, butedit, obj, opt = generic_crud(Maintenance_event, request, fields, fmt)
    
    todos_registos = []
    for code in sorted(list(set(Maintenance_event.lst))):
        if code in Maintenance_event.obj:
            m = Maintenance_event.obj[code]
            todos_registos.append({"id": m.id, "eq_id": m.equipment_id, "type_id": m.maintenance_type_id, "date": m.maintenance_date})

    if opt == 'insert' or option == 'insert':
        return render_template("maintenance.html", butshow=butshow, butedit=butedit, id=Maintenance_event.get_id(0), equipment_id="", maintenance_type_id="", maintenance_date="", extra_info="", todos_registos=todos_registos)
    
    m_date = getattr(obj, Maintenance_event.att[3]) if obj else ""
    if hasattr(m_date, "strftime"): m_date = m_date.strftime("%d/%m/%Y")

    return render_template("maintenance.html", butshow=butshow, butedit=butedit, 
                           id=getattr(obj, Maintenance_event.att[0]) if obj else Maintenance_event.get_id(0), 
                           equipment_id=getattr(obj, Maintenance_event.att[1]) if obj else "", 
                           maintenance_type_id=getattr(obj, Maintenance_event.att[2]) if obj else "", 
                           maintenance_date=m_date, 
                           extra_info=getattr(obj, Maintenance_event.att[4]) if obj else "", todos_registos=todos_registos)

# 5. tipos de manutenção
@app.route("/maintenance_types", methods=["POST", "GET"])
def maintenance_types():
    fields = ["equipment_id"]
    fmt = lambda next_id, f: f"{next_id};{f['equipment_id']}"
    
    option = request.args.get("option")
    if option == "current":
        target_id = request.args.get("id")
        if target_id: Maintenance_Type.current(int(target_id))

    butshow, butedit, obj, opt = generic_crud(Maintenance_Type, request, fields, fmt)
    
    todos_registos = []
    for code in sorted(list(set(Maintenance_Type.lst))):
        if code in Maintenance_Type.obj:
            mt = Maintenance_Type.obj[code]
            todos_registos.append({"id": mt.id, "eq_id": mt.equipment_id})

    if opt == 'insert' or option == 'insert':
        return render_template("maintenance_types.html", butshow=butshow, butedit=butedit, id=Maintenance_Type.get_id(0), equipment_id="", todos_registos=todos_registos)
    
    return render_template("maintenance_types.html", butshow=butshow, butedit=butedit, 
                           id=getattr(obj, Maintenance_Type.att[0]) if obj else Maintenance_Type.get_id(0), 
                           equipment_id=getattr(obj, Maintenance_Type.att[1]) if obj else "", todos_registos=todos_registos)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)