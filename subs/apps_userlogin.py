from flask import Flask, render_template, request, session
from classes.userlogin import Userlogin
from app import db_path2 

def apps_userlogin():
    ulogin = session.get("user")
    user_id = Userlogin.get_user_id(ulogin)
    
    if ulogin is None:
        return render_template("index.html", ulogin=None)

    prev_option = session.get("prev_option", "")

    group = ""
    if hasattr(Userlogin, 'obj') and Userlogin.obj and user_id in Userlogin.obj:
        group = Userlogin.obj[user_id].usergroup

    if "visualizando_id" not in session:
        session["visualizando_id"] = user_id

    if group not in ["administrador_pessoal", "chefe", "operador_equipamento", "operador_manutencao"]:
        session["visualizando_id"] = user_id

    select_id = request.values.get("select_id")
    if select_id:
        try: 
            session["visualizando_id"] = int(select_id)
        except ValueError: 
            pass

    try:
        Userlogin.current(session["visualizando_id"])
    except Exception:
        pass
        
    butshow = "enabled"
    butedit = "disabled"
    option = request.values.get("option", "")
    msg = ""
    
    grupos_validos = ["administrador_pessoal", "chefe", "operador_equipamento", "operador_manutencao"]
    
    id_atual_na_tela = session.get("visualizando_id")
    
    if group not in ["chefe", "administrador_pessoal"]:
        try:
            if id_atual_na_tela and int(id_atual_na_tela) != int(user_id):
                butshow = "disabled"   # Tranca o botão Editar no HTML
                
                if option == "edit":
                    option = ""        # Limpa a ação
                    msg = "Erro: Não tem permissão para editar este utilizador!"
        except (ValueError, TypeError):
            butshow = "disabled"


    if option == "edit":
        butshow = "disabled"
        butedit = "enabled"
        
    elif option == "delete":
        obj = Userlogin.current()
        if obj:
            if obj.id == user_id:
                msg = "Erro: Não pode eliminar a sua própria conta!"
            else:
                try:
                    id_para_eliminar = int(obj.id)
                    Userlogin.remove(id_para_eliminar)
                    
                    Userlogin.read(db_path2)
                    Userlogin.first()
                    
                    obj_novo = Userlogin.current()
                    session["visualizando_id"] = obj_novo.id if obj_novo else user_id
                    msg = "Utilizador eliminado com sucesso!"
                except Exception as e:
                    msg = f"Erro ao eliminar: {str(e)}"
                    
    elif option == "insert":
        butshow = "disabled"
        butedit = "enabled"
        
    elif option == 'cancel':
        pass
        
    elif prev_option == 'insert' and option == 'save':
        username_novo = request.values.get("user", "")
        group_novo = request.values.get("usergroup", "").strip()
        pass_novo = request.values.get("password", "")

        if group_novo not in grupos_validos:
            msg = f"Erro: O grupo '{group_novo}' não existe no sistema! Insira um grupo reconhecido."
            butshow = "disabled"
            butedit = "enabled"
            option = "insert" 
        elif username_novo:
            try:
                senha_cripto = Userlogin.set_password(pass_novo)
                novo_utilizador = Userlogin(0, username_novo, group_novo, senha_cripto)

                Userlogin.obj[username_novo] = novo_utilizador
                Userlogin.insert(username_novo)
                
                if username_novo in Userlogin.obj: 
                    del Userlogin.obj[username_novo]
                    
                Userlogin.read(db_path2)
                Userlogin.last()
                
                obj_novo = Userlogin.current()
                if obj_novo: 
                    session["visualizando_id"] = obj_novo.id
                    
                msg = "Utilizador adicionado com sucesso!"
            except Exception as e:
                Userlogin.read(db_path2)
                msg = f"Erro ao inserir na base de dados: {str(e)}"
        else:
            msg = "Erro: O nome de utilizador não pode estar vazio!"
            butshow = "disabled"
            butedit = "enabled"
            option = "insert"

    
    elif prev_option == 'edit' and option == 'save':
        obj = Userlogin.current()
        if obj:
            user_input = request.values.get("user", "")
            usergroup_input = request.values.get("usergroup", "").strip()
            password_input = request.values.get("password", "")

            if usergroup_input and usergroup_input not in grupos_validos:
                msg = f"Erro: O grupo '{usergroup_input}' não é reconhecido pelo sistema."
                butshow = "disabled"
                butedit = "enabled"
                option = "edit"
            else:
                try:
                    id_para_atualizar = int(obj.id)
                    permissao_para_gravar = False

                    # CASO 1: Chefes / Administradores
                    if group in ["chefe", "administrador_pessoal"]:
                        permissao_para_gravar = True
                        if user_input: 
                            obj._user = user_input
                        if usergroup_input: 
                            obj._usergroup = usergroup_input
                        if password_input != "": 
                            obj._password = Userlogin.set_password(password_input)
                    
                    # CASO 2: Operadores (Faltava este bloco no teu!)
                    else:
                        if id_para_atualizar == int(user_id):
                            if password_input != "": 
                                obj._password = Userlogin.set_password(password_input)
                                permissao_para_gravar = True
                            else:
                                msg = "Aviso: Nenhuma alteração efetuada (campo da senha vazio)."
                        else:
                            msg = "Erro: Não tem permissão para alterar os dados de outros utilizadores!"

                    if permissao_para_gravar:
                        Userlogin.update(id_para_atualizar)
                        msg = "Alterações gravadas com sucesso!"
                        
                    Userlogin.read(db_path2)
                except Exception as e:
                    Userlogin.read(db_path2)
                    msg = f"Erro ao atualizar base de dados: {str(e)}"


    if option not in ["insert", "edit"]:
        try:
            if option == "first": Userlogin.first()
            elif option == "previous": Userlogin.previous()
            elif option == "next": Userlogin.nextrec()
            elif option == "last": Userlogin.last()
        except Exception:
            pass
        
    obj_novo = Userlogin.current()
    if obj_novo: 
        session["visualizando_id"] = obj_novo.id

    if option in ["insert", "edit", "save", "cancel"]:
        session["prev_option"] = option
    else:
        session["prev_option"] = ""

    try:
        Userlogin.current(session["visualizando_id"])
        obj = Userlogin.current()
    except Exception:
        obj = None
    
    tamanho = len(Userlogin.obj) if (hasattr(Userlogin, 'obj') and Userlogin.obj) else 0

    if option == 'insert' or tamanho == 0 or not obj:
        id_atual, user, usergroup, password = "", "", "", ""
    else:
        try:
            id_atual = obj._id
            user = obj._user
            usergroup = obj._usergroup
            password = ""
        except Exception:
            id_atual, user, usergroup, password = "", "", "", ""
        
    lista_pessoas = list(Userlogin.obj.values()) if (hasattr(Userlogin, 'obj') and Userlogin.obj) else []

    return render_template(
        "userlogin.html", 
        butshow=butshow, 
        butedit=butedit, 
        id=id_atual, 
        user=user, 
        usergroup=usergroup, 
        password=password, 
        ulogin=ulogin, 
        group=group,
        msg=msg,
        pessoas=lista_pessoas
    )
