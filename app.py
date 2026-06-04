from flask import Flask, render_template, request
import os
from datafile import filename

from classes.operator import Operator
from classes.equipment import Equipment
from classes.maintenance_event import Maintenance_event
from classes.maintenance_type import Maintenance_Type
from classes.equipment_operator import Equipment_Operator
from classes.userlogin import Userlogin

from subs.apps_gform import apps_gform 
from subs.apps_subform import apps_subform 
from subs.apps_userlogin import apps_userlogin

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

db_path = os.path.join(filename, 'equipment_management.db') if not filename.endswith('/') else filename + 'equipment_management.db'

Operator.read(db_path)
Equipment.read(db_path)
Maintenance_event.read(db_path)
Maintenance_Type.read(db_path)
Equipment_Operator.read(db_path)
Userlogin.read(db_path)

def validar_foreign_keys(eq_id=None, op_id=None, type_id=None):
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


@app.route("/dashboard")
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

            if filtro_ano != "Todos" and ano != filtro_ano: continue
            if filtro_mes != "Todos" and mes != filtro_mes: continue

            custo = float(uo.cost) if getattr(uo, 'cost', None) else 0.0
            custo_total_periodo += custo

            chave_tempo = f"{ano}-{mes}" if filtro_ano == "Todos" else f"Dia {partes[2]}" if len(partes) > 2 else data_str
            cronograma_dados[chave_tempo] = cronograma_dados.get(chave_tempo, 0.0) + custo

            op_id = uo.operator_id
            op_name = Operator.obj[int(op_id)]._title if int(op_id) in Operator.obj else f"OP #{op_id}"
            util_op[op_name] = util_op.get(op_name, 0) + 1

            eq_id = uo.equipment_id
            eq_name = Equipment.obj[int(eq_id)]._name if int(eq_id) in Equipment.obj else f"EQ #{eq_id}"
            ef = float(uo.get_efficiency_score) if hasattr(uo, 'get_efficiency_score') else 75.0
            if eq_name not in eficiencia_por_equip: eficiencia_por_equip[eq_name] = []
            eficiencia_por_equip[eq_name].append(ef)

    for c in Maintenance_event.lst:
        if c in Maintenance_event.obj:
            m = Maintenance_event.obj[c]
            eq_id = m.equipment_id
            eq_name = Equipment.obj[int(eq_id)]._name if int(eq_id) in Equipment.obj else f"EQ #{eq_id}"
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
        anos_disponiveis=anos_disponiveis, meses_disponiveis=meses_disponiveis,
        filtro_ano=filtro_ano, filtro_mes=filtro_mes, custo_total_periodo=custo_total_periodo,
        g1_x=g1_eixo_x, g1_y=g1_eixo_y,
        g2_labels=g2_labels, g2_y=g2_percentagens, g2_txt=g2_absolutos,
        g3_labels=g3_labels, g3_y=g3_percentagens, g3_txt=g3_absolutos,
        g_azul_labels=g_azul_labels, g_azul_valores=g_azul_valores
    )


@app.route("/operators", methods=["POST", "GET"])
def operators():
    option = request.args.get("option")
    prev = request.args.get("prev")
    butshow, butedit = "", "disabled"

    if option == "current" and request.args.get("id"):
        Operator.current(int(request.args.get("id")))
    elif option == "first": Operator.first()
    elif option == "previous": Operator.previous()
    elif option == "next": Operator.nextrec()
    elif option == "last": Operator.last()
    elif option == "delete" and Operator.current():
        Operator.remove(Operator.current().id)
        Operator.first()
    elif option in ["edit", "insert"]:
        butshow, butedit = "disabled", ""
    elif option == "save":
        if prev == "insert":
            nid = Operator.get_id(0)
            Operator.obj[nid] = Operator.from_string(f"{nid};{request.form['title']};{request.form['category']};{request.form['birth_date']}")
            Operator.lst.append(nid)
            Operator.insert(nid)
            Operator.last()
        elif prev == "edit" and Operator.current():
            obj = Operator.current()
            obj.title, obj.category, obj.birth_date = request.form['title'], request.form['category'], request.form['birth_date']
            Operator.update(obj.id)

    todos = [{"id": Operator.obj[c].id, "title": Operator.obj[c].title, "category": Operator.obj[c].category, "age": Operator.obj[c].age} for c in sorted(list(set(Operator.lst))) if c in Operator.obj]
    obj = None if option == "insert" or prev == "insert" and option == "save" else Operator.current()

    return render_template("operators.html", butshow=butshow, butedit=butedit, 
                           id=obj.id if obj else Operator.get_id(0), 
                           title=obj.title if obj else "", 
                           category=obj.category if obj else "", 
                           birth_date=obj.birth_date if obj else "", todos_registos=todos)


@app.route("/equipments", methods=["POST", "GET"])
def equipments():
    option = request.args.get("option")
    prev = request.args.get("prev")
    butshow, butedit = "", "disabled"

    if option == "current" and request.args.get("id"):
        Equipment.current(int(request.args.get("id")))
    elif option == "first": Equipment.first()
    elif option == "previous": Equipment.previous()
    elif option == "next": Equipment.nextrec()
    elif option == "last": Equipment.last()
    elif option == "delete" and Equipment.current():
        Equipment.remove(Equipment.current().id)
        Equipment.first()
    elif option in ["edit", "insert"]:
        butshow, butedit = "disabled", ""
    elif option == "save":
        if prev == "insert":
            nid = Equipment.get_id(0)
            Equipment.obj[nid] = Equipment.from_string(f"{nid};{request.form['name']};{request.form['creation_date']}")
            Equipment.lst.append(nid)
            Equipment.insert(nid)
            Equipment.last()
        elif prev == "edit" and Equipment.current():
            obj = Equipment.current()
            obj.name, obj.creation_date = request.form['name'], request.form['creation_date']
            Equipment.update(obj.id)

    todos = [Equipment.obj[c] for c in sorted(list(set(Equipment.lst))) if c in Equipment.obj]
    obj = None if option == "insert" or prev == "insert" and option == "save" else Equipment.current()

    return render_template("equipments.html", butshow=butshow, butedit=butedit, 
                           id=obj.id if obj else Equipment.get_id(0), 
                           name=obj.name if obj else "", 
                           creation_date=obj.creation_date if obj else "", todos_registos=todos)


@app.route("/utilization", methods=["POST", "GET"])
def utilization():
    option = request.args.get("option")
    prev = request.args.get("prev")
    butshow, butedit = "", "disabled"

    if option == "current" and request.args.get("id"):
        Equipment_Operator.current(int(request.args.get("id")))
    elif option == "first": Equipment_Operator.first()
    elif option == "previous": Equipment_Operator.previous()
    elif option == "next": Equipment_Operator.nextrec()
    elif option == "last": Equipment_Operator.last()
    elif option == "delete" and Equipment_Operator.current():
        Equipment_Operator.remove(Equipment_Operator.current().id)
        Equipment_Operator.first()
    elif option in ["edit", "insert"]:
        butshow, butedit = "disabled", ""
    elif option == "save":
        eq_id = request.form.get('equipment_id')
        op_id = request.form.get('operator_id')
        
        if validar_foreign_keys(eq_id=eq_id, op_id=op_id):
            if prev == "insert":
                nid = Equipment_Operator.get_id(0)
                Equipment_Operator.obj[nid] = Equipment_Operator.from_string(f"{nid};{eq_id};{op_id};{request.form['utilization_date']};{request.form['cost']}")
                Equipment_Operator.lst.append(nid)
                Equipment_Operator.insert(nid)
                Equipment_Operator.last()
            elif prev == "edit" and Equipment_Operator.current():
                obj = Equipment_Operator.current()
                obj.equipment_id, obj.operator_id, obj.utilization_date, obj.cost = int(eq_id), int(op_id), request.form['utilization_date'], request.form['cost']
                Equipment_Operator.update(obj.id)
        else:
            butshow, butedit = "disabled", ""
            option = prev

    todos = [{"id": Equipment_Operator.obj[c].id, "eq_id": Equipment_Operator.obj[c].equipment_id, "op_id": Equipment_Operator.obj[c].operator_id, "cost": Equipment_Operator.obj[c].cost, "efficiency": Equipment_Operator.obj[c].get_efficiency_score} for c in sorted(list(set(Equipment_Operator.lst))) if c in Equipment_Operator.obj]
    obj = None if option == "insert" or prev == "insert" and option == "save" else Equipment_Operator.current()
    
    u_date = obj.utilization_date if obj else ""
    if hasattr(u_date, "strftime"): u_date = u_date.strftime("%d/%m/%Y")

    return render_template("utilization.html", butshow=butshow, butedit=butedit, 
                           id=obj.id if obj else Equipment_Operator.get_id(0), 
                           equipment_id=obj.equipment_id if obj else "", 
                           operator_id=obj.operator_id if obj else "", 
                           utilization_date=u_date, cost=obj.cost if obj else "", todos_registos=todos)


@app.route("/maintenance", methods=["POST", "GET"])
def maintenance():
    option = request.args.get("option")
    prev = request.args.get("prev")
    butshow, butedit = "", "disabled"

    if option == "current" and request.args.get("id"):
        Maintenance_event.current(int(request.args.get("id")))
    elif option == "first": Maintenance_event.first()
    elif option == "previous": Maintenance_event.previous()
    elif option == "next": Maintenance_event.nextrec()
    elif option == "last": Maintenance_event.last()
    elif option == "delete" and Maintenance_event.current():
        Maintenance_event.remove(Maintenance_event.current().id)
        Maintenance_event.first()
    elif option in ["edit", "insert"]:
        butshow, butedit = "disabled", ""
    elif option == "save":
        eq_id = request.form.get('equipment_id')
        type_id = request.form.get('maintenance_type_id')

        if validar_foreign_keys(eq_id=eq_id, type_id=type_id):
            if prev == "insert":
                nid = Maintenance_event.get_id(0)
                Maintenance_event.obj[nid] = Maintenance_event.from_string(f"{nid};{eq_id};{type_id};{request.form['maintenance_date']};{request.form['extra_info']}")
                Maintenance_event.lst.append(nid)
                Maintenance_event.insert(nid)
                Maintenance_event.last()
            elif prev == "edit" and Maintenance_event.current():
                obj = Maintenance_event.current()
                obj.equipment_id, obj.maintenance_type_id, obj.maintenance_date, obj.extra_info = int(eq_id), int(type_id), request.form['maintenance_date'], request.form['extra_info']
                Maintenance_event.update(obj.id)
        else:
            butshow, butedit = "disabled", ""
            option = prev

    todos = [{"id": Maintenance_event.obj[c].id, "eq_id": Maintenance_event.obj[c].equipment_id, "type_id": Maintenance_event.obj[c].maintenance_type_id, "date": Maintenance_event.obj[c].maintenance_date} for c in sorted(list(set(Maintenance_event.lst))) if c in Maintenance_event.obj]
    obj = None if option == "insert" or prev == "insert" and option == "save" else Maintenance_event.current()

    m_date = obj.maintenance_date if obj else ""
    if hasattr(m_date, "strftime"): m_date = m_date.strftime("%d/%m/%Y")

    return render_template("maintenance.html", butshow=butshow, butedit=butedit, 
                           id=obj.id if obj else Maintenance_event.get_id(0), 
                           equipment_id=obj.equipment_id if obj else "", 
                           maintenance_type_id=obj.maintenance_type_id if obj else "", 
                           maintenance_date=m_date, extra_info=obj.extra_info if obj else "", todos_registos=todos)


@app.route("/maintenance_types", methods=["POST", "GET"])
def maintenance_types():
    option = request.args.get("option")
    prev = request.args.get("prev")
    butshow, butedit = "", "disabled"

    if option == "current" and request.args.get("id"):
        Maintenance_Type.current(int(request.args.get("id")))
    elif option == "first": Maintenance_Type.first()
    elif option == "previous": Maintenance_Type.previous()
    elif option == "next": Maintenance_Type.nextrec()
    elif option == "last": Maintenance_Type.last()
    elif option == "delete" and Maintenance_Type.current():
        Maintenance_Type.remove(Maintenance_Type.current().id)
        Maintenance_Type.first()
    elif option in ["edit", "insert"]:
        butshow, butedit = "disabled", ""
    elif option == "save":
        eq_id = request.form.get('equipment_id')
        
        if validar_foreign_keys(eq_id=eq_id):
            if prev == "insert":
                nid = Maintenance_Type.get_id(0)
                Maintenance_Type.obj[nid] = Maintenance_Type.from_string(f"{nid};{eq_id}")
                Maintenance_Type.lst.append(nid)
                Maintenance_Type.insert(nid)
                Maintenance_Type.last()
            elif prev == "edit" and Maintenance_Type.current():
                obj = Maintenance_Type.current()
                obj.equipment_id = int(eq_id)
                Maintenance_Type.update(obj.id)
        else:
            butshow, butedit = "disabled", ""
            option = prev

    todos = [{"id": Maintenance_Type.obj[c].id, "eq_id": Maintenance_Type.obj[c].equipment_id} for c in sorted(list(set(Maintenance_Type.lst))) if c in Maintenance_Type.obj]
    obj = None if option == "insert" or prev == "insert" and option == "save" else Maintenance_Type.current()

    return render_template("maintenance_types.html", butshow=butshow, butedit=butedit, 
                           id=obj.id if obj else Maintenance_Type.get_id(0), 
                           equipment_id=obj.equipment_id if obj else "", todos_registos=todos)

#login
@app.route("/")
def index():
    return render_template("index.html", ulogin=session.get("user"))
@app.route("/login")
def login():
    return render_template("login.html", user= "", password="", ulogin=session.get("user"),resul = "")
@app.route("/logoff")
def logoff():
    session.pop("user",None)
    return render_template("index.html", ulogin=session.get("user"))
@app.route("/chklogin", methods=["post","get"])
def chklogin():
    user = request.form["user"]
    password = request.form["password"]
    resul = Userlogin.chk_password(user, password)
    if resul == "Valid":
        session["user"] = user
        return render_template("index.html", ulogin=session.get("user"))
    return render_template("login.html", user=user, password = password, ulogin=session.get("user"),resul = resul)

@app.route("/gform/<cname>", methods=["post","get"])
def gform(cname):
    return apps_gform(cname)
@app.route("/subform/<cname>", methods=["post","get"])
def subform(cname):
    return apps_subform(cname)
@app.route("/Userlogin", methods=["post","get"])
def userlogin():
    return apps_userlogin()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
