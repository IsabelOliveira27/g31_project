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
db_path2 = os.path.join(filename, 'users.db') if not filename.endswith('/') else filename + 'users.db'

Operator.read(db_path)
Equipment.read(db_path)
Maintenance_event.read(db_path)
Maintenance_type.read(db_path)
Equipment_operator.read(db_path)
Userlogin.read(db_path2)


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
def dashboard():
    filtro_ano = request.args.get("ano", "Todos")
    filtro_mes = request.args.get("mes", "Todos")
    vista = request.args.get("vista", "utilizacao")

    anos_disponiveis = ["2024", "2025", "2026"]
    meses_disponiveis = [
        {"num": "01", "nome": "Jan"}, {"num": "02", "nome": "Fev"},
        {"num": "03", "nome": "Mar"}, {"num": "04", "nome": "Abr"},
        {"num": "05", "nome": "Mai"}, {"num": "06", "nome": "Jun"},
        {"num": "07", "nome": "Jul"}, {"num": "08", "nome": "Ago"},
        {"num": "09", "nome": "Set"}, {"num": "10", "nome": "Out"},
        {"num": "11", "nome": "Nov"}, {"num": "12", "nome": "Dez"}
    ]

    def extrair_ano_mes_dia(data_str):
        data_str = str(data_str).strip()
        if "/" in data_str:
            partes = data_str.split("/")
            if len(partes) >= 3:
                return partes[2], partes[1], partes[0]
        elif "-" in data_str:
            partes = data_str.split("-")
            if len(partes) >= 3:
                if len(partes[0]) == 4:
                    return partes[0], partes[1], partes[2]
                else:
                    return partes[2], partes[1], partes[0]
        return "2026", "05", "01"

    tabela_registos = []
    global_avarias = {}
    
    
    
    for c in getattr(Maintenance_event, 'lst', []):
        if c in getattr(Maintenance_event, 'obj', {}):
            m_obj = Maintenance_event.obj[c]
            eq_id_s = str(getattr(m_obj, 'equipment_id', '')).strip()
            if eq_id_s and eq_id_s != "None":
                global_avarias[eq_id_s] = global_avarias.get(eq_id_s, 0) + 1

    if vista == "utilizacao":
        custo_total = 0.0
        maior_custo = 0.0
        cronograma = {}
        cronograma_horas = {}
        operador_custos = {}
        equip_type_custos = {}
        categoria_custos = {}

        for c in getattr(Equipment_operator, 'lst', []):
            if c in getattr(Equipment_operator, 'obj', {}):
                uo = Equipment_operator.obj[c]
                ano, mes, dia = extrair_ano_mes_dia(getattr(uo, 'utilization_date', ''))

                if (filtro_ano != "Todos" and ano != filtro_ano): continue
                if (filtro_mes != "Todos" and mes != filtro_mes): continue

                custo = float(uo.cost) if getattr(uo, 'cost', None) else 0.0
                horas = float(getattr(uo, 'hours_used', 8.0))
                custo_total += custo
                if custo > maior_custo:
                    maior_custo = custo

                chave_tempo = f"{ano}-{mes}" if filtro_ano == "Todos" else f"Dia {dia}"
                cronograma[chave_tempo] = cronograma.get(chave_tempo, 0.0) + custo
                cronograma_horas[chave_tempo] = cronograma_horas.get(chave_tempo, 0.0) + horas

                op_id = str(uo.operator_id).strip()
                op_name = f"Op. #{op_id}"
                try:
                    if int(op_id) in Operator.obj:
                        op_name = getattr(Operator.obj[int(op_id)], 'title', getattr(Operator.obj[int(op_id)], '_title', op_name))
                except:
                    pass
                operador_custos[op_name] = operador_custos.get(op_name, 0.0) + custo

                eq_id = str(uo.equipment_id).strip()
                t_tipo = "1"
                eq_name = f"Equip. #{eq_id}"
                try:
                    if int(eq_id) in Equipment.obj:
                        eq_obj = Equipment.obj[int(eq_id)]
                        t_tipo = str(getattr(eq_obj, 'type', getattr(eq_obj, '_type', '1'))).strip()
                        eq_name = getattr(eq_obj, 'name', getattr(eq_obj, '_name', eq_name))
                except:
                    pass
                
                label_tipo = f"Tipo {t_tipo}"
                equip_type_custos[label_tipo] = equip_type_custos.get(label_tipo, 0.0) + custo
                
                cat = getattr(uo, 'category', 'Geral')
                categoria_custos[cat] = categoria_custos.get(cat, 0.0) + custo

                dt_original = getattr(uo, 'utilization_date', '')
                dt_formatada = f"{dia}/{mes}/{ano}" if (ano and mes and dia) else dt_original

                tabela_registos.append({
                    "col1": dt_formatada, "col2": eq_name, "col3": op_name,
                    "col4": f"{custo:.2f} €", "col5": cat
                })

        g1_x = sorted(list(cronograma.keys()))
        g1_y = [cronograma[k] for k in g1_x]
        g1_y2 = [cronograma_horas[k] for k in g1_x]

        ops_m = sorted(operador_custos.items(), key=lambda x: x[1], reverse=True)[:5]
        ops_m = list(reversed(ops_m))
        g2_labels = [x[0] for x in ops_m]
        g2_valores = [x[1] for x in ops_m]

        tipos_m = sorted(equip_type_custos.items(), key=lambda x: x[1], reverse=True)
        g3_labels = [x[0] for x in tipos_m]
        g3_valores = [x[1] for x in tipos_m]
        
        cats_m = sorted(categoria_custos.items(), key=lambda x: x[1], reverse=True)[:5]
        g5_labels = [x[0] for x in cats_m]
        g5_valores = [x[1] for x in cats_m]

        media_custo = (custo_total / len(tabela_registos)) if tabela_registos else 0.0

        return render_template(
            "dashboard.html", ulogin=session.get("user"),
            anos_disponiveis=anos_disponiveis, meses_disponiveis=meses_disponiveis,
            filtro_ano=filtro_ano, filtro_mes=filtro_mes, vista=vista,
            kpi1=f"{custo_total:.2f} €", title1="Custo Total Operacional",
            kpi2=f"{media_custo:.2f} €", title2="Custo Médio por Turno",
            kpi3=f"{maior_custo:.2f} €", title3="Maior Custo Registado",
            g1_x=g1_x, g1_y=g1_y, g1_y2=g1_y2, g2_labels=g2_labels, g2_valores=g2_valores,
            g3_labels=g3_labels, g3_valores=g3_valores, g5_labels=g5_labels, g5_valores=g5_valores,
            tabela_registos=tabela_registos,
            h1="Data", h2="Equipamento", h3="Operador", h4="Custo", h5="Categoria"
        )

    else:
        avarias_totais = 0
        manut_equip = {}
        contagem_tipos = {}
        equip_avarias = {}
        equip_custos = {}
        cronograma_manut = {}

        for c_op in getattr(Equipment_operator, 'lst', []):
            if c_op in getattr(Equipment_operator, 'obj', {}):
                uo_o = Equipment_operator.obj[c_op]
                eq_s = str(uo_o.equipment_id).strip()
                cst_val = float(uo_o.cost) if getattr(uo_o, 'cost', None) else 0.0
                equip_custos[eq_s] = equip_custos.get(eq_s, 0.0) + cst_val

        for c in getattr(Maintenance_event, 'lst', []):
            if c in getattr(Maintenance_event, 'obj', {}):
                m = Maintenance_event.obj[c]
                dt_m = getattr(m, 'maintenance_date', '')
                ano, mes, dia = extrair_ano_mes_dia(dt_m)

                if (filtro_ano != "Todos" and ano != filtro_ano): continue
                if (filtro_mes != "Todos" and mes != filtro_mes): continue

                eq_id = str(m.equipment_id).strip()
                if not eq_id or eq_id == "None": continue

                avarias_totais += 1
                equip_avarias[eq_id] = equip_avarias.get(eq_id, 0) + 1

                chave_tempo = f"{ano}-{mes}" if filtro_ano == "Todos" else f"Dia {dia}"
                cronograma_manut[chave_tempo] = cronograma_manut.get(chave_tempo, 0) + 1

                eq_name = f"Equip. #{eq_id}"
                try:
                    if int(eq_id) in Equipment.obj:
                        eq_name = getattr(Equipment.obj[int(eq_id)], 'name', getattr(Equipment.obj[int(eq_id)], '_name', eq_name))
                except:
                    pass

                manut_equip[eq_name] = manut_equip.get(eq_name, 0) + 1

                tipo_f = str(getattr(m, 'maintenance_type_id', 'Geral')).split('.')[0]
                contagem_tipos[tipo_f] = contagem_tipos.get(tipo_f, 0) + 1

                dt_formatada = f"{dia}/{mes}/{ano}" if (ano and mes and dia) else dt_m

                tabela_registos.append({
                    "col1": dt_formatada, "col2": eq_name, "col3": f"Falha {tipo_f}",
                    "col4": getattr(m, 'extra_info', 'Sem notas')
                })

        manut_ord = sorted(manut_equip.items(), key=lambda x: x[1], reverse=True)[:5]
        manut_ord = list(reversed(manut_ord))
        g1_x = [x[0] for x in manut_ord]
        g1_y = [x[1] for x in manut_ord]

        tipos_ord = sorted(contagem_tipos.items(), key=lambda x: x[1], reverse=True)[:5]
        g2_labels = [f"Falha {x[0]}" for x in tipos_ord]
        g2_valores = [x[1] for x in tipos_ord]

        g5_x = sorted(list(cronograma_manut.keys()))
        g5_y = [cronograma_manut[k] for k in g5_x]

        sc_x, sc_y, sc_sizes, sc_colors, sc_text = [], [], [], [], []
        cores = {"1": "#3b82f6", "2": "#10b981", "3": "#f59e0b", "4": "#ef4444", "5": "#8b5cf6"}
        max_c = max(equip_custos.values()) if equip_custos else 1.0

        dados_boxplot_custos = { "1":[], "2":[], "3":[], "4":[], "5":[] }

        if hasattr(Equipment, 'obj') and Equipment.obj:
            for eq_id, eq_obj in Equipment.obj.items():
                id_str = str(eq_id).strip()
                avs = global_avarias.get(id_str, 0)
                if avs == 0: continue

                c_date = str(getattr(eq_obj, 'creation_date', '2024-01-01')).strip()
                ano_c, mes_c = 2024, 1
                numeros = re.findall(r'\d+', c_date)
                if len(numeros) >= 2:
                    if len(numeros[0]) == 4:
                        ano_c, mes_c = int(numeros[0]), int(numeros[1])
                    elif len(numeros[2]) == 4:
                        ano_c, mes_c = int(numeros[2]), int(numeros[1])

                idade = (2026 - ano_c) * 12 + (6 - mes_c)
                if idade < 0: idade = 0

                cst = equip_custos.get(id_str, 0.0)
                t_tipo = str(getattr(eq_obj, 'type', getattr(eq_obj, '_type', '1'))).strip()

                if t_tipo in dados_boxplot_custos:
                    dados_boxplot_custos[t_tipo].append(cst)

                sc_x.append(idade)
                sc_y.append(avs)
                sc_sizes.append(6 + int((cst / max_c) * 20))
                sc_colors.append(cores.get(t_tipo, "#94a3b8"))
                
                eq_real_n = getattr(eq_obj, 'name', getattr(eq_obj, '_name', id_str))
                sc_text.append(f"Máquina: {eq_real_n}<br>Tipo: {t_tipo}<br>Idade: {idade} m<br>Avarias: {avs}")

        heatmap_encoded = None
        try:
            plt.clf()
            plt.close('all')
            fig, ax = plt.subplots(figsize=(4.5, 2.6), facecolor='#151f32')
            ax.set_facecolor('#151f32')
            
            lista_valores_plot = [dados_boxplot_custos[k] if dados_boxplot_custos[k] else [0] for k in ["1", "2", "3", "4", "5"]]
            medias = [np.mean(l) for l in lista_valores_plot]
            categorias = ['Tipo 1', 'Tipo 2', 'Tipo 3', 'Tipo 4', 'Tipo 5']
            
            ax.bar(categorias, medias, color=['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'], alpha=0.6, width=0.45)
            ax.plot(categorias, medias, color='#ffffff', marker='o', linewidth=1.2, markersize=3.5)
            
            ax.set_title("Severidade Orçamental por Categoria", color='#cbd5e1', fontsize=11, pad=8, weight='bold')
            ax.set_ylabel("Custo Médio (€)", color='#94a3b8', fontsize=9, labelpad=4)
            
            ax.tick_params(axis='both', colors='#cbd5e1', labelsize=9)
            ax.grid(axis='y', color='#1e293b', linestyle='--', linewidth=0.5)
            for spine in ax.spines.values(): spine.set_visible(False)
                
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
            "dashboard.html", ulogin=session.get("user"),
            anos_disponiveis=anos_disponiveis, meses_disponiveis=meses_disponiveis,
            filtro_ano=filtro_ano, filtro_mes=filtro_mes, vista=vista,
            kpi1=str(avarias_totais), title1="Nº Total de Avarias",
            kpi2="-", title2="-", kpi3="-", title3="-",
            g1_x=g1_x, g1_y=g1_y, g2_labels=g2_labels, g2_valores=g2_valores,
            g5_x=g5_x, g5_y=g5_y,
            sc_x=sc_x, sc_y=sc_y, sc_sizes=sc_sizes, sc_colors=sc_colors, sc_text=sc_text,
            heatmap_img=heatmap_encoded, tabela_registos=tabela_registos,
            h1="Data Falha", h2="Equipamento Crítico", h3="Manutenção Efetuada", h4="Descrição / Extra Info"
        )
    
    
    
@app.route('/gestao-assets')
def gestao_assets():
    return render_template('gestao_assets.html',ulogin=session.get("user"))
    


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
        return render_template("operators.html", ulogin=session.get("user"), butshow=butshow, butedit=butedit, id=Operator.get_id(0), title="", category="", birth_date="", todos_registos=todos_registos)
        
    return render_template("operators.html", ulogin=session.get("user"), butshow=butshow, butedit=butedit, 
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
        return render_template("equipments.html", ulogin=session.get("user"), butshow=butshow, butedit=butedit, opt_state="insert", 
                               id=Equipment.get_id(0), name="", creation_date="", type="", todos_registos=todos_registos)
    
    return render_template("equipments.html", ulogin=session.get("user"), butshow=butshow, butedit=butedit, opt_state=opt,
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
        return render_template("utilization.html", ulogin=session.get("user"), butshow=butshow, butedit=butedit, id=Equipment_operator.get_id(0), equipment_id="", operator_id="", utilization_date="", cost="", todos_registos=todos_registos)
    
    return render_template("utilization.html", ulogin=session.get("user"), butshow=butshow, butedit=butedit, 
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
        return render_template("maintenance.html", ulogin=session.get("user"), butshow=butshow, butedit=butedit, id=Maintenance_event.get_id(0), equipment_id="", maintenance_type_id="", maintenance_date="", extra_info="", todos_registos=todos_registos)
    
    return render_template("maintenance.html", ulogin=session.get("user"), butshow=butshow, butedit=butedit, 
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
        return render_template("maintenance_types.html", ulogin=session.get("user"), butshow=butshow, butedit=butedit, id=Maintenance_type.get_id(0), equipment_id="", todos_registos=todos_registos)
        
    return render_template("maintenance_types.html", ulogin=session.get("user"), butshow=butshow, butedit=butedit, 
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
    return render_template("index.html", ulogin=session.get("user"), group=session.get("group"))

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
        
        id_do_utilizador = Userlogin.user_id
        objeto_utilizador = Userlogin.obj[id_do_utilizador]
        
        session['group'] = objeto_utilizador.usergroup
        
        return render_template("index.html", ulogin=session.get("user"),group=session.get("group") )
    return render_template("login.html", user=user, password = password, ulogin=session.get("user"),resul = resul)



@app.route("/gform/<cname>", methods=["post","get"])
def gform(cname):
    return apps_gform(cname)

@app.route("/subform/<cname>", methods=["post","get"])
def subform(cname):
    return apps_subform(cname)

@app.route("/Userlogin", methods=["post","get"])
def userlogin():
    return apps_userlogin(db_path2)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    
