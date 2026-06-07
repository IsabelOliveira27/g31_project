from flask import Flask, render_template, request, session
from classes.userlogin import Userlogin

prev_option = ""

def apps_userlogin():
    global prev_option
    ulogin = session.get("user")
    user_id = Userlogin.get_user_id(ulogin)
    
    if (ulogin != None):
        if user_id in Userlogin.obj:
            group = Userlogin.obj[user_id].usergroup
        else:
            group = "visitante"

        if "visualizando_id" not in session:
            session["visualizando_id"] = user_id

        if group not in ["chefe", "administrador_pessoal"]:
            session["visualizando_id"] = user_id

        select_id = request.args.get("select_id")
        if select_id:
            session["visualizando_id"] = int(select_id)

        Userlogin.current(session["visualizando_id"])
            
        butshow = "enabled"
        butedit = "disabled"
        option = request.args.get("option")
        msg = ""
        
        if option == "edit":
            butshow = "disabled"
            butedit = "enabled"
            
        elif option == "delete":
            obj = Userlogin.current()
            if obj:
                if obj.id == user_id:
                    msg = "Erro: Não pode eliminar a sua própria conta!"
                else:
                    Userlogin.remove(obj.id)
                    # Força a releitura do ficheiro/BD após eliminar
                    if hasattr(Userlogin, 'read'): Userlogin.read()
                    elif hasattr(Userlogin, 'load'): Userlogin.load()
                    
                    Userlogin.first()
                    obj_novo = Userlogin.current()
                    session["visualizando_id"] = obj_novo.id if obj_novo else user_id
                        
        elif option == "insert":
            butshow = "disabled"
            butedit = "enabled"
            
        elif option == 'cancel':
            pass
            
        elif prev_option == 'insert' and option == 'save':
            # Cria o objeto com os dados do formulário
            obj = Userlogin(0, request.form["user"], request.form["usergroup"], \
                            Userlogin.set_password(request.form["password"]))
            
            # CORREÇÃO CRÍTICA: Passa o objeto inteiro 'obj' e não apenas o ID 0
            Userlogin.insert(obj)
            
            # Força a releitura imediata para a tabela lateral ver o novo utilizador
            if hasattr(Userlogin, 'read'): Userlogin.read()
            elif hasattr(Userlogin, 'load'): Userlogin.load()
            
            Userlogin.last()
            obj_novo = Userlogin.current()
            if obj_novo:
                session["visualizando_id"] = obj_novo.id
            
        elif prev_option == 'edit' and option == 'save':
            obj = Userlogin.current()
            if obj:
                if group in ["chefe", "administrador_pessoal"]:
                    obj.usergroup = request.form["usergroup"]
                if request.form["password"] != "":
                    obj.password = Userlogin.set_password(request.form["password"])
                
                Userlogin.update(obj.id)
                

                if hasattr(Userlogin, 'read'): Userlogin.read()
                elif hasattr(Userlogin, 'load'): Userlogin.load()
                

        elif option == "first":
            Userlogin.first()
            obj_novo = Userlogin.current()
            if obj_novo: session["visualizando_id"] = obj_novo.id
            
        elif option == "previous":
            Userlogin.previous()
            obj_novo = Userlogin.current()
            if obj_novo: session["visualizando_id"] = obj_novo.id
            
        elif option == "next":
            Userlogin.nextrec()  
            obj_novo = Userlogin.current()
            if obj_novo: session["visualizando_id"] = obj_novo.id
            
        elif option == "last":
            Userlogin.last()
            obj_novo = Userlogin.current()
            if obj_novo: session["visualizando_id"] = obj_novo.id
            
        elif option == 'exit':
            session.pop("visualizando_id", None)
            return render_template("index.html", ulogin=session.get("user"))


        prev_option = option
        Userlogin.current(session["visualizando_id"])
        obj = Userlogin.current()
        
        tamanho = len(Userlogin.obj) if hasattr(Userlogin, 'obj') else len(Userlogin.lst)

        if option == 'insert' or tamanho == 0 or not obj:
            id_atual = ""
            user = ""
            usergroup = ""
            password = ""
        else:
            id_atual = obj.id
            user = obj.user
            usergroup = obj.usergroup
            password = ""
            
        return render_template(
            "userlogin.html", 
            butshow=butshow, 
            butedit=butedit, 
            id=id_atual, 
            user=user, 
            usergroup=usergroup, 
            password=password, 
            ulogin=session.get("user"), 
            group=group,
            msg=msg,
            pessoas=Userlogin.obj.values() if hasattr(Userlogin, 'obj') else Userlogin.lst
        )
    else:
        return render_template("index.html", ulogin=ulogin)     
