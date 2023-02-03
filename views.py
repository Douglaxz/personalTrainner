# importação de dependencias
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory
import time
from datetime import date, timedelta
from personal import app, db
from models import tb_user,\
    tb_usertype,\
    tb_academia,\
    tb_aluno
from helpers import \
    FormularPesquisa, \
    FormularioUsuarioTrocarSenha,\
    FormularioUsuario, \
    FormularioUsuarioVisualizar, \
    FormularioTipoUsuarioEdicao,\
    FormularioTipoUsuarioVisualizar,\
    FormularioAcademiaEdicao,\
    FormularioAcademiaVisualizar,\
    FormularioAlunoEdicao,\
    FormularioAlunoVisualizar
# ITENS POR PÁGINA
from config import ROWS_PER_PAGE, CHAVE
from flask_bcrypt import generate_password_hash, Bcrypt, check_password_hash

import string
import random
import numbers

##################################################################################################################################
#GERAL
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: index
#FUNÇÃO: redirecionar para página principal
#PODE ACESSAR: todos os usuários
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/')
def index():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))        
    return render_template('index.html', titulo='Bem vindos')

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: logout
#FUNÇÃO: remover dados de sessão e deslogar ususários
#PODE ACESSAR: todos os usuários
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session['usuario_logado'] = None
    flash('Logout efetuado com sucesso','success')
    return redirect(url_for('login'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: login
#FUNÇÃO: direcionar para formulário de login
#PODE ACESSAR: todos os usuários
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/login')
def login():
    return render_template('login1.html')

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: autenticar
#FUNÇÃO: autenticar usuário
#PODE ACESSAR: todos os usuários
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/autenticar', methods = ['GET', 'POST'])
def autenticar():
    usuario = tb_user.query.filter_by(login_user=request.form['usuario']).first()
    senha = check_password_hash(usuario.password_user,request.form['senha'])
    if usuario:
        if senha:
            session['usuario_logado'] = usuario.login_user
            session['nomeusuario_logado'] = usuario.name_user
            session['tipousuario_logado'] = usuario.cod_usertype
            session['coduser_logado'] = usuario.cod_user
            flash(usuario.name_user + ' Usuário logado com sucesso','success')
            #return redirect('/')
            return redirect('/')
        else:
            flash('Verifique usuário e senha', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Usuário não logado com sucesso','success')
        return redirect(url_for('login'))

##################################################################################################################################
#USUARIOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: usuario
#FUNÇÃO: tela do sistema para mostrar os usuários cadastrados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/usuario', methods=['POST','GET'])
def usuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('usuario')))        
    form = FormularPesquisa()
    page = request.args.get('page', 1, type=int)
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data

    if pesquisa == "" or pesquisa == None:    
        usuarios = tb_user.query\
        .join(tb_usertype, tb_usertype.cod_usertype==tb_user.cod_usertype)\
        .add_columns(tb_user.login_user, tb_user.cod_user, tb_user.name_user, tb_user.status_user, tb_usertype.desc_usertype)\
        .order_by(tb_user.name_user)\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)
    else:
        usuarios = tb_user.query\
        .filter(tb_user.name_user.ilike(f'%{pesquisa}%'))\
        .join(tb_usertype, tb_usertype.cod_usertype==tb_user.cod_usertype)\
        .add_columns(tb_user.login_user, tb_user.cod_user, tb_user.name_user, tb_user.status_user, tb_usertype.desc_usertype)\
        .order_by(tb_user.name_user)\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)


    return render_template('usuarios.html', titulo='Usuários', usuarios=usuarios, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoUsuario
#FUNÇÃO: mostrar o formulário de cadastro de usuário
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/novoUsuario')
def novoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoUsuario')))     
    form = FormularioUsuario()
    return render_template('novoUsuario.html', titulo='Novo Usuário', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarUsuario
#FUNÇÃO: inserir informações do usuário no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarUsuario', methods=['POST',])
def criarUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login',proxima=url_for('criarUsuario')))      
    form = FormularioUsuario(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('novoUsuario'))
    nome  = form.nome.data
    status = form.status.data
    login = form.login.data
    tipousuario = form.tipousuario.data
    email = form.email.data
    #criptografar senha
    senha = generate_password_hash("teste@12345").decode('utf-8')
    usuario = tb_user.query.filter_by(name_user=nome).first()
    if usuario:
        flash ('Usuário já existe','danger')
        return redirect(url_for('index')) 
    novoUsuario = tb_user(name_user=nome, status_user=status, login_user=login, cod_usertype=tipousuario, password_user=senha, email_user=email)
    db.session.add(novoUsuario)
    db.session.commit()
    flash('Usuário criado com sucesso','success')
    return redirect(url_for('usuario'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarUsuarioexterno - NÃO DISPONIVEL NESTA VERSAL
#FUNÇÃO: inserir informações do usuário no banco de dados realizam cadastro pela área externa
#PODE ACESSAR: novos usuários
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/criarUsuarioexterno', methods=['POST',])
def criarUsuarioexterno():    
    nome  = request.form['nome']
    status = 0
    email = request.form['email']
    localarroba = email.find("@")
    login = email[0:localarroba]
    tipousuario = 2
    #criptografar senha
    senha = generate_password_hash(request.form['senha']).decode('utf-8')
    usuario = tb_user.query.filter_by(name_user=nome).first()
    if usuario:
        flash ('Usuário já existe','danger')
        return redirect(url_for('login')) 
    novoUsuario = tb_user(name_user=nome, status_user=status, login_user=login, cod_usertype=tipousuario, password_user=senha, email_user=email)
    db.session.add(novoUsuario)
    db.session.commit()
    flash('Usuário criado com sucesso, favor logar com ele','success')
    return redirect(url_for('login'))  

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarUsuario
#FUNÇÃO: mostrar formulário de visualização dos usuários cadastrados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarUsuario/<int:id>')
def visualizarUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarUsuario')))    
    usuario = tb_user.query.filter_by(cod_user=id).first()
    form = FormularioUsuarioVisualizar()
    form.nome.data = usuario.name_user
    form.status.data = usuario.status_user
    form.login.data = usuario.login_user
    form.tipousuario.data = usuario.cod_usertype
    form.email.data = usuario.email_user
    return render_template('visualizarUsuario.html', titulo='Visualizar Usuário', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarUsuario
#FUNÇÃO: mostrar formulário de edição dos usuários cadastrados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/editarUsuario/<int:id>')
def editarUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarUsuario/<int:id>')))  
    usuario = tb_user.query.filter_by(cod_user=id).first()
    form = FormularioUsuario()
    form.nome.data = usuario.name_user
    form.status.data = usuario.status_user
    form.login.data = usuario.login_user
    form.tipousuario.data = usuario.cod_usertype
    form.email.data = usuario.email_user
    return render_template('editarUsuario.html', titulo='Editar Usuário', id=id, form=form)    
       
#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarUsuario
#FUNÇÃO: alterar as informações dos usuários no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarUsuario', methods=['POST',])
def atualizarUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarUsuario')))          
    form = FormularioUsuario(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('atualizarUsuario'))
    id = request.form['id']
    usuario = tb_user.query.filter_by(cod_user=request.form['id']).first()
    usuario.name_user = form.nome.data
    usuario.status_user = form.status.data
    usuario.login_user = form.login.data
    usuario.cod_uertype = form.tipousuario.data
    db.session.add(usuario)
    db.session.commit()
    flash('Usuário alterado com sucesso','success')
    return redirect(url_for('visualizarUsuario', id=request.form['id']))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarSenhaUsuario
#FUNÇÃO: formulário para edição da tela do usuário
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarSenhaUsuario/')
def editarSenhaUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarUsuario')))    
    form = FormularioUsuarioTrocarSenha()
    return render_template('trocarsenha.html', titulo='Trocar Senha', id=id, form=form)  

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: trocarSenhaUsuario
#FUNÇÃO: alteração da senha do usuário no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/trocarSenhaUsuario', methods=['POST',])
def trocarSenhaUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarUsuario')))          
    form = FormularioUsuarioTrocarSenha(request.form)
    if form.validate_on_submit():
        id = session['coduser_logado']
        usuario = tb_user.query.filter_by(cod_user=id).first()
        if form.senhaatual.data != usuario.password_user:
            flash('senha atual incorreta','danger')
            return redirect(url_for('editarSenhaUsuario'))

        if form.senhaatual.data != usuario.password_user:
            flash('senha atual incorreta','danger')
            return redirect(url_for('editarSenhaUsuario')) 

        if form.novasenha1.data != form.novasenha2.data:
            flash('novas senhas não coincidem','danger')
            return redirect(url_for('editarSenhaUsuario')) 
        usuario.password_user = generate_password_hash(form.novasenha1.data).decode('utf-8')
        db.session.add(usuario)
        db.session.commit()
        flash('senha alterada com sucesso!','success')
    else:
        flash('senha não alterada!','danger')
    return redirect(url_for('editarSenhaUsuario')) 

##################################################################################################################################
#TIPO DE USUARIOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: tipousuario
#FUNÇÃO: tela do sistema para mostrar os tipos de usuários cadastrados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/tipousuario', methods=['POST','GET'])
def tipousuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('tipousuario')))         
    page = request.args.get('page', 1, type=int)
    form = FormularPesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    
    if pesquisa == "" or pesquisa == None:     
        tiposusuario = tb_usertype.query.order_by(tb_usertype.desc_usertype)\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        tiposusuario = tb_usertype.query.order_by(tb_usertype.desc_usertype)\
        .filter(tb_usertype.desc_usertype.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('tipousuarios.html', titulo='Tipo Usuário', tiposusuario=tiposusuario, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoTipoUsuario
#FUNÇÃO: mostrar o formulário de cadastro de tipo de usuário
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoTipoUsuario')
def novoTipoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoTipoUsuario'))) 
    form = FormularioTipoUsuarioEdicao()
    return render_template('novoTipoUsuario.html', titulo='Novo Tipo Usuário', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarTipoUsuario
#FUNÇÃO: inserir informações do tipo de usuário no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarTipoUsuario', methods=['POST',])
def criarTipoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarTipoUsuario')))     
    form = FormularioTipoUsuarioEdicao(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarTipoUsuario'))
    desc  = form.descricao.data
    status = form.status.data
    tipousuario = tb_usertype.query.filter_by(desc_usertype=desc).first()
    if tipousuario:
        flash ('Tipo Usuário já existe','danger')
        return redirect(url_for('tipousuario')) 
    novoTipoUsuario = tb_usertype(desc_usertype=desc, status_usertype=status)
    flash('Tipo de usuário criado com sucesso!','success')
    db.session.add(novoTipoUsuario)
    db.session.commit()
    return redirect(url_for('tipousuario'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarTipoUsuario
#FUNÇÃO: mostrar formulário de visualização dos tipos de usuários cadastrados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarTipoUsuario/<int:id>')
def visualizarTipoUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarTipoUsuario')))  
    tipousuario = tb_usertype.query.filter_by(cod_usertype=id).first()
    form = FormularioTipoUsuarioVisualizar()
    form.descricao.data = tipousuario.desc_usertype
    form.status.data = tipousuario.status_usertype
    return render_template('visualizarTipoUsuario.html', titulo='Visualizar Tipo Usuário', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarTipoUsuario
##FUNÇÃO: mostrar formulário de edição dos tipos de usuários cadastrados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarTipoUsuario/<int:id>')
def editarTipoUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarTipoUsuario')))  
    tipousuario = tb_usertype.query.filter_by(cod_usertype=id).first()
    form = FormularioTipoUsuarioEdicao()
    form.descricao.data = tipousuario.desc_usertype
    form.status.data = tipousuario.status_usertype
    return render_template('editarTipoUsuario.html', titulo='Editar Tipo Usuário', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarTipoUsuario
#FUNÇÃO: alterar as informações dos tipos de usuários no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarTipoUsuario', methods=['POST',])
def atualizarTipoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarTipoUsuario')))      
    form = FormularioTipoUsuarioEdicao(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        tipousuario = tb_usertype.query.filter_by(cod_usertype=request.form['id']).first()
        tipousuario.desc_usertype = form.descricao.data
        tipousuario.status_usertype = form.status.data
        db.session.add(tipousuario)
        db.session.commit()
        flash('Tipo de usuário atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarTipoUsuario', id=request.form['id']))    

##################################################################################################################################
#ACADEMIA
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: academia
#FUNÇÃO: tela do sistema para mostrar as academias cadastradas
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/academia', methods=['POST','GET'])
def academia():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('academia')))         
    page = request.args.get('page', 1, type=int)
    form = FormularPesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    if pesquisa == "" or pesquisa == None:     
        academias = tb_academia.query.order_by(tb_academia.nome_academia)\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        academias = tb_academia.query.order_by(tb_academia.nome_academia)\
        .filter(tb_academia.nome_academia.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('academias.html', titulo='Academias', academias=academias, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoAcademia
#FUNÇÃO: mostrar o formulário de cadastro de academia
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoAcademia')
def novoAcademia():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoAcademia'))) 
    form = FormularioAcademiaEdicao()
    return render_template('novoAcademia.html', titulo='Nova Academia', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarAcademia
#FUNÇÃO: inserir informações do academia no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarAcademia', methods=['POST',])
def criarAcademia():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarAcademia')))     
    form = FormularioAcademiaEdicao(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarAcademia'))
    nome  = form.nome.data
    endereco  = form.endereco.data
    status = form.status.data
    academia = tb_academia.query.filter_by(nome_academia=nome).first()
    if academia:
        flash ('Academia já existe','danger')
        return redirect(url_for('academia')) 
    novoAcademia = tb_academia(nome_academia=nome, end_academia=endereco, status_academia=status)
    flash('Academia criado com sucesso!','success')
    db.session.add(novoAcademia)
    db.session.commit()
    return redirect(url_for('academia'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarAcademia
#FUNÇÃO: mostrar formulário de visualização as academias cadastrados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarAcademia/<int:id>')
def visualizarAcademia(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarAcademia')))  
    academia = tb_academia.query.filter_by(cod_academia=id).first()
    form = FormularioAcademiaVisualizar()
    form.nome.data = academia.nome_academia
    form.endereco.data = academia.end_academia
    form.status.data = academia.status_academia
    return render_template('visualizarAcademia.html', titulo='Visualizar Academia', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarAcademia
##FUNÇÃO: mostrar formulário de edição das academias cadastrados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarAcademia/<int:id>')
def editarAcademia(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarAcademia')))  
    academia = tb_academia.query.filter_by(cod_academia=id).first()
    form = FormularioAcademiaEdicao()
    form.nome.data = academia.nome_academia
    form.endereco.data = academia.end_academia
    form.status.data = academia.status_academia
    return render_template('editarAcademia.html', titulo='Editar Academia', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarAcademia
#FUNÇÃO: alterar as informações dos academia no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarAcademia', methods=['POST',])
def atualizarAcademia():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarAcademia')))      
    form = FormularioAcademiaEdicao(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        academia = tb_academia.query.filter_by(cod_academia=request.form['id']).first()
        academia.nome_academia = form.nome.data
        academia.end_academia = form.endereco.data
        academia.status_academia = form.status.data
        db.session.add(academia)
        db.session.commit()
        flash('Academia atualizada com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarAcademia', id=request.form['id']))

##################################################################################################################################
#ALUNO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: aluno
#FUNÇÃO: tela do sistema para mostrar os alunos cadastradoss
#PODE ACESSAR: usuários do tipo administrador e personal
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/aluno', methods=['POST','GET'])
def aluno():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('aluno')))         
    page = request.args.get('page', 1, type=int)
    form = FormularPesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    if pesquisa == "" or pesquisa == None:     
        alunos = tb_aluno.query.order_by(tb_aluno.nome_aluno)\
        .filter(tb_aluno.cod_user == session['coduser_logado'])\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        alunos = tb_aluno.query.order_by(tb_aluno.nome_aluno)\
        .filter(tb_aluno.nome_aluno.ilike(f'%{pesquisa}%'))\
        .filter(tb_aluno.cod_user == session['usuario_logado'])\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('alunos.html', titulo='Alunos', alunos=alunos, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoAluno
#FUNÇÃO: mostrar o formulário de cadastro de alunos
#PODE ACESSAR: usuários do tipo administrador e personal
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoAluno')
def novoAluno():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoAluno'))) 
    form = FormularioAlunoEdicao()
    return render_template('novoAluno.html', titulo='Novo Aluno', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarAluno
#FUNÇÃO: inserir informações do aluno no banco de dados
#PODE ACESSAR: usuários do tipo administrador e persoal
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarAluno', methods=['POST',])
def criarAluno():
    
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarAluno')))     
    form = FormularioAlunoEdicao(request.form)
    
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('novoAluno'))
    form = FormularioAlunoEdicao(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarAluno'))
    nome  = form.nome.data
    endereco  = form.endereco.data
    telefone  = form.telefone.data
    datanascimento  = form.datanascimento.data
    observacoes  = form.observacoes.data
    academia = form.academia.data
    status = form.status.data
    usuario = session['coduser_logado']
    diavencimento = form.diavencimento.data
    aluno = tb_aluno.query.filter_by(nome_aluno=nome).first()
    horarioinicio = form.horarioinicio.data
    horariofinal = form.horariofinal.data
    dom = form.diadom.data
    seg = form.diaseg.data
    ter = form.diater.data
    qua = form.diaqua.data
    qui = form.diaqui.data
    sex = form.diasex.data
    sab = form.diasab.data    
    if aluno:
        flash ('Aluno já existe','danger')
        return redirect(url_for('aluno')) 
    novoAluno = tb_aluno(nome_aluno=nome,end_aluno=endereco,status_aluno=status,datanasc_aluno=datanascimento,cod_user=usuario,cod_academia=academia,obs_aluno=observacoes,telefone_aluno=telefone,diavenc_aluno=diavencimento,hrinicio_aluno=horarioinicio,hrfinal_aluno=horariofinal,dom_aluno = dom,seg_aluno = seg,ter_aluno = ter,qua_aluno = qua,qui_aluno = qui,sex_aluno = sex,sab_aluno = sab)
    flash('Aluno criado com sucesso!','success')
    db.session.add(novoAluno)
    db.session.commit()
    return redirect(url_for('aluno'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarAluno
#FUNÇÃO: mostrar formulário de visualização os alunos cadastrados
#PODE ACESSAR: usuários do tipo administrador e persoal
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarAluno/<int:id>')
def visualizarAluno(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarAluno')))  
    aluno = tb_aluno.query.filter_by(cod_aluno=id).first()
    form = FormularioAlunoVisualizar()
    form.nome.data = aluno.nome_aluno
    form.endereco.data = aluno.end_aluno
    form.telefone.data = aluno.telefone_aluno
    form.academia.data = aluno.cod_academia
    form.status.data = aluno.status_aluno
    form.datanascimento.data = aluno.datanasc_aluno.strftime("%d/%m/%Y")
    form.observacoes.data = aluno.obs_aluno
    form.diavencimento.data = aluno.diavenc_aluno
    form.horarioinicio.data = aluno.hrinicio_aluno
    form.horariofinal.data = aluno.hrfinal_aluno
    form.diadom.data = aluno.dom_aluno
    form.diaseg.data = aluno.seg_aluno
    form.diater.data = aluno.ter_aluno
    form.diaqua.data = aluno.qua_aluno
    form.diaqui.data = aluno.qui_aluno
    form.diasex.data = aluno.sex_aluno
    form.diasab.data = aluno.sab_aluno
    return render_template('visualizarAluno.html', titulo='Visualizar Aluno', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarAluno
##FUNÇÃO: mostrar formulário de edição dos alunos cadastrados
#PODE ACESSAR: usuários do tipo administrador e persoal
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarAluno/<int:id>')
def editarAluno(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarAluno')))  
    aluno = tb_aluno.query.filter_by(cod_aluno=id).first()
    form = FormularioAlunoEdicao()
    form.nome.data = aluno.nome_aluno
    form.endereco.data = aluno.end_aluno
    form.telefone.data = aluno.telefone_aluno
    form.academia.data = aluno.cod_academia
    form.status.data = aluno.status_aluno
    form.datanascimento.data = aluno.datanasc_aluno
    form.observacoes.data = aluno.obs_aluno
    form.diavencimento.data = aluno.diavenc_aluno
    form.horarioinicio.data = aluno.hrinicio_aluno
    form.horariofinal.data = aluno.hrfinal_aluno
    form.diadom.data = aluno.dom_aluno
    form.diaseg.data = aluno.seg_aluno
    form.diater.data = aluno.ter_aluno
    form.diaqua.data = aluno.qua_aluno
    form.diaqui.data = aluno.qui_aluno
    form.diasex.data = aluno.sex_aluno
    form.diasab.data = aluno.sab_aluno    
    return render_template('editarAluno.html', titulo='Editar Aluno', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarAluno
#FUNÇÃO: alterar as informações dos alunos no banco de dados
#PODE ACESSAR: usuários do tipo administrador e personal
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarAluno', methods=['POST','GET'])
def atualizarAluno():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarAluno')))      
    form = FormularioAlunoEdicao(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        aluno = tb_aluno.query.filter_by(cod_aluno=request.form['id']).first()
        aluno.nome_aluno = form.nome.data
        aluno.end_aluno = form.endereco.data
        aluno.status_aluno = form.status.data
        aluno.telefone_aluno = form.telefone.data
        aluno.datanasc_aluno = form.datanascimento.data
        aluno.obs_aluno = form.observacoes.data
        aluno.cod_academia = form.academia.data
        aluno.diavenc_aluno = form.diavencimento.data
        aluno.hrinicio_aluno = form.horarioinicio.data
        aluno.hrfinal_aluno = form.horariofinal.data
        aluno.dom_aluno = form.diadom.data
        aluno.seg_aluno = form.diaseg.data
        aluno.ter_aluno = form.diater.data
        aluno.qua_aluno = form.diaqua.data
        aluno.qui_aluno = form.diaqui.data
        aluno.sex_aluno = form.diasex.data
        aluno.sab_aluno = form.diasab.data

        db.session.add(aluno)
        db.session.commit()
        flash('Aluno atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarAluno', id=request.form['id']))