from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datafile import filename
import os
import datetime
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import re

from classes.operator import Operator
from classes.equipment import Equipment
from classes.maintenance_event import Maintenance_event
from classes.maintenance_type import Maintenance_type
from classes.equipment_operator import Equipment_operator
from classes.userlogin import Userlogin

from subs.apps_gform import apps_gform 
from subs.apps_subform import apps_subform 
from subs.apps_userlogin import apps_userlogin

app = Flask(__name__)
app.secret_key = 'CHAVE_SUPER_SECRETA_E_SEGURA_MB_FIC_2025'

db_path = os.path.join(filename, 'MB_&_FIC.db') if not filename.endswith('/') else filename + 'MB_&_FIC.db'


Operator.read(db_path)
Equipment.read(db_path)
Maintenance_event.read(db_path)
Maintenance_type.read(db_path)
Equipment_operator.read(db_path)
Userlogin.read(db_path)



prev_option = ""

def validar_foreign_keys(eq_id=None, op_id=None, type_id=None):
    try:
        if eq_id is not None:
            if int(eq_id) <= 0 or int(eq_id) not in Equipment.obj:
                return False
        if op_id is not None:
            if int(op_id) <= 0 or int(op_id) not in Operator.obj:
                return False
        if type_id is not None:
            if int(type_id) <= 0 or int(type_id) not in Maintenance_type.obj:
                return False
        return True
    except (ValueError, TypeError):
        return False

def generic_crud(cls, request, form_fields, strobj_format):
    global prev_option
    butshow, butedit = "", "disabled" 
    option = request.args.get("option")
    id_att = cls.att[0]
    
    search_val = request.args.get("search_val")
    search_att = request.args.get("search_att")
    
    if option == "search" and search_val and search_att:
        real_att = next((a for a in cls.att if a == search_att or a.lstrip('_') == search_att.lstrip('_')), cls.att[1])
        if str(search_val).isdigit():
            search_val = int(search_val)
            
        ids_encontrados = cls.getlines(real_att, search_val)
        if ids_encontrados:
            cls.set_filter({real_att: [search_val]})
        else:
            cls.set_filter({real_att: ["__NOT_FOUND__"]})
            cls.lst = []
            cls.pos = 0
        option = None 
        
    elif option == "clear_search":
        cls.set_filter({})
        cls.first()
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
        
        partes = strobj.split(';')
        if cls == Equipment_operator and not validar_foreign_keys(eq_id=partes[1], op_id=partes[2]):
            return butshow, butedit, cls.current(), "insert"
        elif cls == Maintenance_event and not validar_foreign_keys(eq_id=partes[1], type_id=partes[2]):
            return butshow, butedit, cls.current(), "insert"
        elif cls == Maintenance_type and not validar_foreign_keys(eq_id=partes[1]):
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
            if cls == Equipment_operator and not validar_foreign_keys(eq_id=request.form.get(form_fields[0]), op_id=request.form.get(form_fields[1])):
                return "disabled", "", obj, "edit"
            elif cls == Maintenance_event and not validar_foreign_keys(eq_id=request.form.get(form_fields[0]), type_id=request.form.get(form_fields[1])):
                return "disabled", "", obj, "edit"
            elif cls == Maintenance_type and not validar_foreign_keys(eq_id=request.form.get(form_fields[0])):
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


@app.route("/dashboard")
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
    contagem_tipos = {}
    equip_avarias = {}
    equip_custos = {}

    for c in Equipment_operator.lst:
        if c in Equipment_operator.obj:
            uo = Equipment_operator.obj[c]
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

            eq_id = str(uo.equipment_id).strip()
            equip_custos[eq_id] = equip_custos.get(eq_id, 0.0) + custo

    for c in Maintenance_event.lst:
        if c in Maintenance_event.obj:
            m = Maintenance_event.obj[c]
            eq_id = str(m.equipment_id).strip()
            if not eq_id or eq_id == "None": continue
            
            eq_name = f"Equip. #{eq_id}"
            try:
                key_id = int(eq_id)
                if key_id in Equipment.obj:
                    eq_name = Equipment.obj[key_id]._name
            except:
                for k, obj in Equipment.obj.items():
                    if str(k).strip() == eq_id:
                        eq_name = obj._name
                        break
            
            manut_equip[eq_name] = manut_equip.get(eq_name, 0) + 1
            equip_avarias[eq_id] = equip_avarias.get(eq_id, 0) + 1

            tipo = str(getattr(m, 'maintenance_type_id', 'Não Definido')).strip()
            contagem_tipos[tipo] = contagem_tipos.get(tipo, 0) + 1

    g1_eixo_x = sorted(list(cronograma_dados.keys())) if cronograma_dados else ["Sem Dados"]
    g1_eixo_y = [cronograma_dados[k] for k in g1_eixo_x] if cronograma_dados else [0]

    manut_ordenadas = sorted(manut_equip.items(), key=lambda x: x[1], reverse=False) if manut_equip else []
    manut_ordenadas = manut_ordenadas[-5:]
    g2_labels = [item[0] for item in manut_ordenadas] if manut_ordenadas else ["Sem Registos"]
    g2_valores = [item[1] for item in manut_ordenadas] if manut_ordenadas else [0]

    tipos_ordenados = sorted(contagem_tipos.items(), key=lambda x: x[1], reverse=True)
    if len(tipos_ordenados) > 4:
        g4_labels = [str(x[0]) for x in tipos_ordenados[:4]] + ["Outros"]
        g4_values = [x[1] for x in tipos_ordenados[:4]] + [sum(x[1] for x in tipos_ordenados[4:])]
    else:
        g4_labels = [str(x[0]) for x in tipos_ordenados] if tipos_ordenados else ["Geral"]
        g4_values = [x[1] for x in tipos_ordenados] if tipos_ordenados else [1]

    scatter_x = []
    scatter_y = []
    scatter_sizes = []
    scatter_colors = []
    scatter_text = []

    mapeamento_cores = {"1": "#3b82f6", "2": "#10b981", "3": "#f59e0b", "4": "#ef4444"}
    custos_validos = [v for v in equip_custos.values() if v > 0]
    max_custo = max(custos_validos) if custos_validos else 1.0

    for eq_id, eq_obj in Equipment.obj.items():
        id_str = str(eq_id).strip()
        c_date = str(getattr(eq_obj, 'creation_date', '2024-01-01')).strip()
        
        numeros = re.findall(r'\d+', c_date)
        ano_c, mes_c = 2024, 1 
        
        if len(numeros) >= 2:
            if len(numeros[0]) == 4: 
                ano_c = int(numeros[0])
                mes_c = int(numeros[1])
            elif len(numeros[2]) == 4: 
                ano_c = int(numeros[2])
                mes_c = int(numeros[1])
        elif len(numeros) == 1 and len(numeros[0]) == 4:
            ano_c = int(numeros[0])

        if mes_c < 1 or mes_c > 12: mes_c = 1
        
        idade_meses = (2026 - ano_c) * 12 + (6 - mes_c)
        if idade_meses < 0: idade_meses = 0

        avarias = equip_avarias.get(id_str, 0)
        custo = equip_custos.get(id_str, 0.0)
        t_tipo = str(getattr(eq_obj, 'type', '1')).strip()

        tamanho_normalizado = 8 + int((custo / max_custo) * 22)

        scatter_x.append(idade_meses)
        scatter_y.append(avarias)
        scatter_sizes.append(tamanho_normalizado)
        scatter_colors.append(mapeamento_cores.get(t_tipo, "#8b5cf6"))
        scatter_text.append(f"Equipamento: {getattr(eq_obj, '_name', id_str)}<br>Idade: {idade_meses} Meses<br>Avarias: {avarias}<br>Custo: {custo:.2f} €")

    heatmap_encoded = None
    try:
        plt.clf()
        plt.close('all')
        
        todas_maquinas = []
        todos_ops = []
        for ut in Equipment_operator.obj.values():
            m_id = str(getattr(ut, 'equipment_id', '')).strip()
            o_id = str(getattr(ut, 'operator_id', '')).strip()
            if m_id and o_id and m_id != "None" and o_id != "None":
                todas_maquinas.append(m_id)
                todos_ops.append(o_id)

        maquinas_finais = sorted(list(set(todas_maquinas)))[:6]
        operadores_finais = sorted(list(set(todos_ops)))[:6]

        if maquinas_finais and operadores_finais:
            matriz_dados = np.zeros((len(operadores_finais), len(maquinas_finais)))
            for ut in Equipment_operator.obj.values():
                m_id = str(getattr(ut, 'equipment_id', '')).strip()
                o_id = str(getattr(ut, 'operator_id', '')).strip()
                if m_id in maquinas_finais and o_id in operadores_finais:
                    matriz_dados[operadores_finais.index(o_id), maquinas_finais.index(m_id)] += 1

            fig, ax = plt.subplots(figsize=(4.0, 2.5), facecolor='#151f32')
            ax.set_facecolor('#151f32')
            cax = ax.matshow(matriz_dados, cmap='YlOrRd')
            
            cbar = fig.colorbar(cax, ax=ax, shrink=0.5)
            cbar.ax.yaxis.set_tick_params(color='#94a3b8', labelcolor='#94a3b8', labelsize=7)
            cbar.outline.set_visible(False)

            ax.set_xticks(np.arange(len(maquinas_finais)))
            ax.set_yticks(np.arange(len(operadores_finais)))
            ax.set_xticklabels(maquinas_finais, color='#94a3b8', fontsize=7)
            ax.set_yticklabels(operadores_finais, color='#94a3b8', fontsize=7)
            ax.tick_params(axis='both', colors='#1e293b', length=0)
            
            for spine in ax.spines.values():
                spine.set_visible(False)
                
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=140, facecolor=fig.get_facecolor(), edgecolor='none')
            buf.seek(0)
            heatmap_encoded = base64.b64encode(buf.getvalue()).decode('utf-8')
            buf.close()
            plt.close(fig)
    except:
        heatmap_encoded = None

    return render_template(
        "dashboard.html",
        ulogin=session.get("ulogin"),
        anos_disponiveis=anos_disponiveis,
        meses_disponiveis=meses_disponiveis,
        filtro_ano=filtro_ano,
        filtro_mes=filtro_mes,
        custo_total_periodo=custo_total_periodo,
        g1_x=g1_eixo_x, g1_y=g1_eixo_y,
        g2_labels=g2_labels, g2_valores=g2_valores,
        g4_labels=g4_labels, g4_values=g4_values,
        sc_x=scatter_x, sc_y=scatter_y, sc_sizes=scatter_sizes, sc_colors=scatter_colors, sc_text=scatter_text,
        heatmap_img=heatmap_encoded
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
    for code in Operator.lst:
        if code in Operator.obj:
            todos_registos.append(Operator.obj[code])
            
    todos_registos.sort(key=lambda x: int(x.id) if str(x.id).isdigit() else x.id)

    if opt == 'insert' or option == 'insert':
        return render_template("operators.html", ulogin=session.get("ulogin"), butshow=butshow, butedit=butedit, id=Operator.get_id(0), title="", category="", birth_date="", todos_registos=todos_registos)
        
    return render_template("operators.html", ulogin=session.get("ulogin"), butshow=butshow, butedit=butedit, 
                           id=getattr(obj, Operator.att[0]) if obj else Operator.get_id(0), 
                           title=getattr(obj, Operator.att[1]) if obj else "", 
                           category=getattr(obj, Operator.att[2]) if obj else "", 
                           birth_date=obj.birth_date if obj else "", todos_registos=todos_registos)


@app.route("/equipments", methods=["POST", "GET"])
def equipments():
    fields = ["name", "creation_date", "type"]
    fmt = lambda next_id, f: f"{next_id};{f['name']};{f['creation_date']};{f['type']}"
    
    option = request.args.get("option")
    if option == "current":
        target_id = request.args.get("id")
        if target_id: Equipment.current(int(target_id))

    butshow, butedit, obj, opt = generic_crud(Equipment, request, fields, fmt)
    
    todos_registos = []
    for code in Equipment.lst:
        if code in Equipment.obj:
            todos_registos.append(Equipment.obj[code])
            
    todos_registos.sort(key=lambda x: int(x.id) if str(x.id).isdigit() else x.id)

    if opt == 'insert' or option == 'insert':
        return render_template("equipments.html", ulogin=session.get("ulogin"), butshow=butshow, butedit=butedit, opt_state="insert", 
                               id=Equipment.get_id(0), name="", creation_date="", type="", todos_registos=todos_registos)
    
    return render_template("equipments.html", ulogin=session.get("ulogin"), butshow=butshow, butedit=butedit, opt_state=opt,
                           id=getattr(obj, Equipment.att[0]) if obj else Equipment.get_id(0), 
                           name=getattr(obj, Equipment.att[1]) if obj else "", 
                           creation_date=obj.creation_date if obj else "", 
                           type=getattr(obj, Equipment.att[3]) if obj else "", 
                           todos_registos=todos_registos)

@app.route("/utilization", methods=["POST", "GET"])
def utilization():
    fields = ["equipment_id", "operator_id", "utilization_date", "cost"]
    fmt = lambda next_id, f: f"{next_id};{f['equipment_id']};{f['operator_id']};{f['utilization_date']};{f['cost']}"
    
    option = request.args.get("option")
    if option == "current":
        target_id = request.args.get("id")
        if target_id: Equipment_operator.current(int(target_id))

    butshow, butedit, obj, opt = generic_crud(Equipment_operator, request, fields, fmt)
    
    todos_registos = []
    for code in Equipment_operator.lst:
        if code in Equipment_operator.obj:
            todos_registos.append(Equipment_operator.obj[code])

    todos_registos.sort(key=lambda x: int(x.id) if str(x.id).isdigit() else x.id)

    if opt == 'insert' or option == 'insert':
        return render_template("utilization.html", ulogin=session.get("ulogin"), butshow=butshow, butedit=butedit, id=Equipment_operator.get_id(0), equipment_id="", operator_id="", utilization_date="", cost="", todos_registos=todos_registos)
    
    return render_template("utilization.html", ulogin=session.get("ulogin"), butshow=butshow, butedit=butedit, 
                           id=getattr(obj, Equipment_operator.att[0]) if obj else Equipment_operator.get_id(0), 
                           equipment_id=getattr(obj, Equipment_operator.att[1]) if obj else "", 
                           operator_id=getattr(obj, Equipment_operator.att[2]) if obj else "", 
                           utilization_date=obj.utilization_date if obj else "", 
                           cost=getattr(obj, Equipment_operator.att[4]) if obj else "", todos_registos=todos_registos)


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
    for code in Maintenance_event.lst:
        if code in Maintenance_event.obj:
            todos_registos.append(Maintenance_event.obj[code])

    todos_registos.sort(key=lambda x: int(x.id) if str(x.id).isdigit() else x.id)

    if opt == 'insert' or option == 'insert':
        return render_template("maintenance.html", ulogin=session.get("ulogin"), butshow=butshow, butedit=butedit, id=Maintenance_event.get_id(0), equipment_id="", maintenance_type_id="", maintenance_date="", extra_info="", todos_registos=todos_registos)
    
    return render_template("maintenance.html", ulogin=session.get("ulogin"), butshow=butshow, butedit=butedit, 
                           id=getattr(obj, Maintenance_event.att[0]) if obj else Maintenance_event.get_id(0), 
                           equipment_id=getattr(obj, Maintenance_event.att[1]) if obj else "", 
                           maintenance_type_id=getattr(obj, Maintenance_event.att[2]) if obj else "", 
                           maintenance_date=obj.maintenance_date if obj else "", 
                           extra_info=getattr(obj, Maintenance_event.att[4]) if obj else "", todos_registos=todos_registos)


@app.route("/maintenance_types", methods=["POST", "GET"])
def maintenance_types():
    fields = ["equipment_id"]
    fmt = lambda next_id, f: f"{next_id};{f['equipment_id']}"
    
    option = request.args.get("option")
    if option == "current":
        target_id = request.args.get("id")
        if target_id: Maintenance_type.current(int(target_id))

    butshow, butedit, obj, opt = generic_crud(Maintenance_type, request, fields, fmt)
    
    todos_registos = []
    for code in Maintenance_type.lst:
        if code in Maintenance_type.obj:
            todos_registos.append(Maintenance_type.obj[code])

    todos_registos.sort(key=lambda x: int(x.id) if str(x.id).isdigit() else x.id)

    if opt == 'insert' or option == 'insert':
        return render_template("maintenance_types.html", ulogin=session.get("ulogin"), butshow=butshow, butedit=butedit, id=Maintenance_type.get_id(0), equipment_id="", todos_registos=todos_registos)
        
    return render_template("maintenance_types.html", ulogin=session.get("ulogin"), butshow=butshow, butedit=butedit, 
                           id=getattr(obj, Maintenance_type.att[0]) if obj else Maintenance_type.get_id(0), 
                           equipment_id=getattr(obj, Maintenance_type.att[1]) if obj else "", todos_registos=todos_registos)


@app.route('/api/suggest_equipments')
def suggest_equipments():
    search_att = request.args.get('att', 'name')
    search_val = request.args.get('val', '').strip().lower()
    if len(search_val) < 3: return jsonify([])
    
    sugestoes = {}
    for eq in Equipment.obj.values():
        val_original = getattr(eq, search_att, None)
        if val_original is not None and search_val in str(val_original).lower():
            sugestoes[str(val_original)] = sugestoes.get(str(val_original), 0) + 1
            
    return jsonify([{"texto": k, "qtd": v} for k, v in sorted(sugestoes.items())])


@app.route('/api/suggest_operators')
def suggest_operators():
    search_att = request.args.get('att', 'title')
    search_val = request.args.get('val', '').strip().lower()
    if len(search_val) < 3: return jsonify([])
    
    sugestoes = {}
    for op in Operator.obj.values():
        val_original = getattr(op, search_att, None)
        if val_original is not None and search_val in str(val_original).lower():
            sugestoes[str(val_original)] = sugestoes.get(str(val_original), 0) + 1
            
    return jsonify([{"texto": k, "qtd": v} for k, v in sorted(sugestoes.items())])


@app.route('/api/suggest_utilization')
def suggest_utilization():
    search_att = request.args.get('att', 'equipment_id')
    search_val = request.args.get('val', '').strip().lower()
    if len(search_val) < 3: return jsonify([])
    
    sugestoes = {}
    for ut in Equipment_operator.obj.values():
        val_original = getattr(ut, search_att, None)
        if val_original is not None and search_val in str(val_original).lower():
            sugestoes[str(val_original)] = sugestoes.get(str(val_original), 0) + 1
            
    return jsonify([{"texto": k, "qtd": v} for k, v in sorted(sugestoes.items())])


@app.route('/api/suggest_maintenance')
def suggest_maintenance():
    search_att = request.args.get('att', 'equipment_id')
    search_val = request.args.get('val', '').strip().lower()
    if len(search_val) < 2: return jsonify([])
    
    sugestoes = {}
    for mt in Maintenance_event.obj.values():
        val_original = getattr(mt, search_att, None)
        if val_original is not None and search_val in str(val_original).lower():
            sugestoes[str(val_original)] = sugestoes.get(str(val_original), 0) + 1
            
    return jsonify([{"texto": k, "qtd": v} for k, v in sorted(sugestoes.items())])

@app.route('/api/suggest_mtypes')
def suggest_mtypes():
    search_att = request.args.get('att', 'id')
    search_val = request.args.get('val', '').strip().lower()
    if len(search_val) < 2: return jsonify([])
    
    sugestoes = {}
    for mtype in Maintenance_type.obj.values():
        val_original = getattr(mtype, search_att, None)
        if val_original is not None and search_val in str(val_original).lower():
            sugestoes[str(val_original)] = sugestoes.get(str(val_original), 0) + 1
            
    return jsonify([{"texto": k, "qtd": v} for k, v in sorted(sugestoes.items())])



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





if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    
