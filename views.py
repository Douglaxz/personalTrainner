# importação de dependencias
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory
import time
from datetime import date, timedelta
from personal import app, db
from models import tb_user,\
    tb_usertype,\
    tb_academia,\
    tb_aluno,\
    tb_agenda,\
    tb_tipopagamento,\
    tb_recebimento
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
    FormularioAlunoVisualizar,\
    FormularioAgendaEdicao,\
    FormularioAgendaVisualizar,\
    FormularioAgendaEdicao1,\
    FormularioAgendaEdicao2,\
    FormularioTipoPagamentoEdicao,\
    FormularioTipoPagamentoVisualizar,\
    FormularioRecebimentoEdicao,\
    FormularioRecebimentoVisualizar
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
    return render_template('login.html')

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
    tipopagamento = form.tipopagamento.data
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
    novoAluno = tb_aluno(nome_aluno=nome,end_aluno=endereco,status_aluno=status,datanasc_aluno=datanascimento,cod_user=usuario,cod_academia=academia,obs_aluno=observacoes,telefone_aluno=telefone,diavenc_aluno=diavencimento,hrinicio_aluno=horarioinicio,hrfinal_aluno=horariofinal,dom_aluno = dom,seg_aluno = seg,ter_aluno = ter,qua_aluno = qua,qui_aluno = qui,sex_aluno = sex,sab_aluno = sab, cod_tipopagamento=tipopagamento)
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
    form.tipopagamento.data = aluno.cod_tipopagamento
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
    form.tipopagamento.data = aluno.cod_tipopagamento
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
        aluno.cod_tipopagamento = form.tipopagamento.data
        db.session.add(aluno)
        db.session.commit()
        flash('Aluno atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarAluno', id=request.form['id']))

##################################################################################################################################
#AGENDA
##################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: agenda
#FUNÇÃO: tela do sistema para mostrar o agendamento dos alunos
#PODE ACESSAR: somente o personal
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/agenda', methods=['POST','GET'])
def agenda():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('aluno')))         
    page = request.args.get('page', 1, type=int)
    form = FormularPesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    if pesquisa == "" or pesquisa == None:     
        agendas = tb_agenda.query.order_by(tb_agenda.data_agenda)\
        .join(tb_aluno, tb_aluno.cod_aluno==tb_agenda.cod_aluno)\
        .join(tb_academia, tb_aluno.cod_academia==tb_academia.cod_academia)\
        .add_columns(tb_aluno.nome_aluno, tb_agenda.data_agenda, tb_academia.nome_academia, tb_agenda.cod_agenda, tb_agenda.status_agenda)\
        .filter(tb_agenda.cod_user == session['coduser_logado'])\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        agendas = tb_agenda.query.order_by(tb_agenda.data_agenda)\
        .join(tb_aluno, tb_aluno.cod_aluno==tb_agenda.cod_aluno)\
        .join(tb_academia, tb_aluno.cod_academia==tb_academia.cod_academia)\
        .add_columns(tb_aluno.nome_aluno, tb_agenda.data_agenda, tb_academia.nome_academia, tb_agenda.cod_agenda, tb_agenda.status_agenda)\
        .filter(tb_agenda.cod_user == session['coduser_logado'])\
        .filter(tb_agenda.data_agenda == pesquisa)\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)   
    usuario = int(session['coduser_logado'])     
    return render_template('agenda.html', titulo='Agenda', agendas=agendas, form=form,usuario=usuario)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoAgenda
#FUNÇÃO: mostrar o formulário de cadastro de agenda
#PODE ACESSAR: usuários do tipo administrador e personal
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoAgenda')
def novoAgenda():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoAgenda'))) 
    form = FormularioAgendaEdicao()
    return render_template('novoAgenda.html', titulo='Nova Agenda', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoAgendaNaoProgramada
#FUNÇÃO: mostrar o formulário de cadastro de agenda para casos não programados
#PODE ACESSAR: usuários do tipo administrador e personal
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoAgendaNaoProgramada', methods=['POST','GET'])
def novoAgendaNaoProgramada():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoAgenda'))) 
    form = FormularioAgendaEdicao2()
    form.aluno.choices = [(aluno.cod_aluno, aluno.nome_aluno) for aluno in tb_aluno.query.filter_by(cod_user=session['coduser_logado']).filter(tb_aluno.status_aluno == 0)]       
    return render_template('novoAgendaNaoProgramada.html', titulo='Nova Agenda', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarAgenda
#FUNÇÃO: inserir informações da agenda no banco de dados
#PODE ACESSAR: área do sistema
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarAgenda', methods=['POST',])
def criarAgenda():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarAgenda')))     
    form = FormularioAgendaEdicao(request.form)
    
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('novoAgenda'))
    
    datainicio = form.datainicio.data
    datafim = form.datafim.data

    if datainicio > datafim:
        flash('A data de inicio é maior que a data de fim ','danger')
        return redirect(url_for('novoAgenda')) 

    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    start_date = (datainicio)
    end_date = (datafim)+ timedelta(days=1)
    for single_date in daterange(start_date, end_date):
        diasemana = single_date.weekday()
        match diasemana:
            case 0:
                temAluno = tb_aluno.query.order_by(tb_aluno.nome_aluno)\
                .filter(tb_aluno.seg_aluno == 1)\
                .filter(tb_aluno.cod_user == session['coduser_logado'])\
                .filter(tb_aluno.status_aluno == 0)
                for aluno in temAluno:
                    agendas = tb_agenda.query.order_by(tb_agenda.data_agenda)\
                    .filter(tb_agenda.cod_aluno == aluno.cod_aluno)\
                    .filter(tb_agenda.data_agenda == single_date)\
                    .filter(tb_agenda.cod_user == session['coduser_logado'])
                    rows = agendas.count()
                    if rows == 0:
                        hora = str(aluno.hrinicio_aluno)
                        hora = hora[0:5]
                        data_em_texto = str(single_date.day) +"/"+ str(single_date.month) +"/"+ str(single_date.year) + " "+ str(hora)
                        data = datetime.strptime(data_em_texto, '%d/%m/%Y %H:%M')
                        novoAgenda= tb_agenda(cod_user=session['coduser_logado'], cod_aluno=aluno.cod_aluno, data_agenda=data, status_agenda=0)
                        db.session.add(novoAgenda)
                        db.session.commit()
            case 1:
                temAluno = tb_aluno.query.order_by(tb_aluno.nome_aluno)\
                .filter(tb_aluno.ter_aluno == 1)\
                .filter(tb_aluno.cod_user == session['coduser_logado'])\
                .filter(tb_aluno.status_aluno == 0)
                for aluno in temAluno:
                    agendas = tb_agenda.query.order_by(tb_agenda.data_agenda)\
                    .filter(tb_agenda.cod_aluno == aluno.cod_aluno)\
                    .filter(tb_agenda.data_agenda == single_date)\
                    .filter(tb_agenda.cod_user == session['coduser_logado'])
                    rows = agendas.count()
                    if rows == 0:
                        hora = str(aluno.hrinicio_aluno)
                        hora = hora[0:5]
                        data_em_texto = str(single_date.day) +"/"+ str(single_date.month) +"/"+ str(single_date.year) + " "+ str(hora)
                        data = datetime.strptime(data_em_texto, '%d/%m/%Y %H:%M')
                        novoAgenda= tb_agenda(cod_user=session['coduser_logado'], cod_aluno=aluno.cod_aluno, data_agenda=data, status_agenda=0)
                        db.session.add(novoAgenda)
                        db.session.commit()     
            case 2:
                temAluno = tb_aluno.query.order_by(tb_aluno.nome_aluno)\
                .filter(tb_aluno.qua_aluno == 1)\
                .filter(tb_aluno.cod_user == session['coduser_logado'])\
                .filter(tb_aluno.status_aluno == 0)
                for aluno in temAluno:
                    agendas = tb_agenda.query.order_by(tb_agenda.data_agenda)\
                    .filter(tb_agenda.cod_aluno == aluno.cod_aluno)\
                    .filter(tb_agenda.data_agenda == single_date)\
                    .filter(tb_agenda.cod_user == session['coduser_logado'])
                    rows = agendas.count()
                    if rows == 0:
                        hora = str(aluno.hrinicio_aluno)
                        hora = hora[0:5]
                        data_em_texto = str(single_date.day) +"/"+ str(single_date.month) +"/"+ str(single_date.year) + " "+ str(hora)
                        data = datetime.strptime(data_em_texto, '%d/%m/%Y %H:%M')
                        novoAgenda= tb_agenda(cod_user=session['coduser_logado'], cod_aluno=aluno.cod_aluno, data_agenda=data, status_agenda=0)
                        db.session.add(novoAgenda)
                        db.session.commit()  
            case 3:
                temAluno = tb_aluno.query.order_by(tb_aluno.nome_aluno)\
                .filter(tb_aluno.qui_aluno == 1)\
                .filter(tb_aluno.cod_user == session['coduser_logado'])\
                .filter(tb_aluno.status_aluno == 0)
                for aluno in temAluno:
                    agendas = tb_agenda.query.order_by(tb_agenda.data_agenda)\
                    .filter(tb_agenda.cod_aluno == aluno.cod_aluno)\
                    .filter(tb_agenda.data_agenda == single_date)\
                    .filter(tb_agenda.cod_user == session['coduser_logado'])
                    rows = agendas.count()
                    if rows == 0:
                        hora = str(aluno.hrinicio_aluno)
                        hora = hora[0:5]
                        data_em_texto = str(single_date.day) +"/"+ str(single_date.month) +"/"+ str(single_date.year) + " "+ str(hora)
                        data = datetime.strptime(data_em_texto, '%d/%m/%Y %H:%M')
                        novoAgenda= tb_agenda(cod_user=session['coduser_logado'], cod_aluno=aluno.cod_aluno, data_agenda=data, status_agenda=0)
                        db.session.add(novoAgenda)
                        db.session.commit()
            case 4:
                temAluno = tb_aluno.query.order_by(tb_aluno.nome_aluno)\
                .filter(tb_aluno.sex_aluno == 1)\
                .filter(tb_aluno.cod_user == session['coduser_logado'])\
                .filter(tb_aluno.status_aluno == 0)
                for aluno in temAluno:
                    agendas = tb_agenda.query.order_by(tb_agenda.data_agenda)\
                    .filter(tb_agenda.cod_aluno == aluno.cod_aluno)\
                    .filter(tb_agenda.data_agenda == single_date)\
                    .filter(tb_agenda.cod_user == session['coduser_logado'])
                    rows = agendas.count()
                    if rows == 0:
                        hora = str(aluno.hrinicio_aluno)
                        hora = hora[0:5]
                        data_em_texto = str(single_date.day) +"/"+ str(single_date.month) +"/"+ str(single_date.year) + " "+ str(hora)
                        data = datetime.strptime(data_em_texto, '%d/%m/%Y %H:%M')
                        novoAgenda= tb_agenda(cod_user=session['coduser_logado'], cod_aluno=aluno.cod_aluno, data_agenda=data, status_agenda=0)
                        db.session.add(novoAgenda)
                        db.session.commit()  
            case 5:
                temAluno = tb_aluno.query.order_by(tb_aluno.nome_aluno)\
                .filter(tb_aluno.sab_aluno == 1)\
                .filter(tb_aluno.cod_user == session['coduser_logado'])\
                .filter(tb_aluno.status_aluno == 0)
                for aluno in temAluno:
                    agendas = tb_agenda.query.order_by(tb_agenda.data_agenda)\
                    .filter(tb_agenda.cod_aluno == aluno.cod_aluno)\
                    .filter(tb_agenda.data_agenda == single_date)\
                    .filter(tb_agenda.cod_user == session['coduser_logado'])
                    rows = agendas.count()
                    if rows == 0:
                        hora = str(aluno.hrinicio_aluno)
                        hora = hora[0:5]
                        data_em_texto = str(single_date.day) +"/"+ str(single_date.month) +"/"+ str(single_date.year) + " "+ str(hora)
                        data = datetime.strptime(data_em_texto, '%d/%m/%Y %H:%M')
                        novoAgenda= tb_agenda(cod_user=session['coduser_logado'], cod_aluno=aluno.cod_aluno, data_agenda=data, status_agenda=0)
                        db.session.add(novoAgenda)
                        db.session.commit()         
            case 6:
                temAluno = tb_aluno.query.order_by(tb_aluno.nome_aluno)\
                .filter(tb_aluno.dom_aluno == 1)\
                .filter(tb_aluno.cod_user == session['coduser_logado'])\
                .filter(tb_aluno.status_aluno == 0)
                for aluno in temAluno:
                    agendas = tb_agenda.query.order_by(tb_agenda.data_agenda)\
                    .filter(tb_agenda.cod_aluno == aluno.cod_aluno)\
                    .filter(tb_agenda.data_agenda == single_date)\
                    .filter(tb_agenda.cod_user == session['coduser_logado'])
                    rows = agendas.count()
                    if rows == 0:
                        hora = str(aluno.hrinicio_aluno)
                        hora = hora[0:5]
                        data_em_texto = str(single_date.day) +"/"+ str(single_date.month) +"/"+ str(single_date.year) + " "+ str(hora)
                        data = datetime.strptime(data_em_texto, '%d/%m/%Y %H:%M')
                        novoAgenda= tb_agenda(cod_user=session['coduser_logado'], cod_aluno=aluno.cod_aluno, data_agenda=data, status_agenda=0)
                        db.session.add(novoAgenda)
                        db.session.commit()                                                                                                                                        
    return redirect(url_for('agenda'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarAgendaNaoProgramada
#FUNÇÃO: mostrar o formulário de cadastro de agenda para casos não programados
#PODE ACESSAR: usuários do tipo administrador e personal
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/criarAgendaNaoProgramada', methods=['POST','GET'])
def criarAgendaNaoProgramada():
    form = FormularioAgendaEdicao2()
    
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarAgenda')))     
    
    if form.horario.data == None or form.aluno.data == None :
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('novoAgendaNaoProgramada'))
       
    data = form.horario.data
    aluno = form.aluno.data
    agendas = tb_agenda.query.order_by(tb_agenda.data_agenda)\
    .filter(tb_agenda.cod_aluno == aluno)\
    .filter(tb_agenda.data_agenda == data)\
    .filter(tb_agenda.cod_user == session['coduser_logado'])
    rows = agendas.count()

    if rows == 0:
        novoAgenda= tb_agenda(cod_user=session['coduser_logado'], cod_aluno=aluno, data_agenda=data, status_agenda=0)
        db.session.add(novoAgenda)
        db.session.commit()
    return redirect(url_for('agenda'))                        

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarAgenda
#FUNÇÃO: visualizar informações da agenda no banco de dados
#PODE ACESSAR: personal
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarAgenda/<int:id>')
def visualizarAgenda(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarAgenda')))  
    agenda = tb_agenda.query.filter_by(cod_agenda=id).first()
    aluno = tb_aluno.query.filter_by(cod_aluno=agenda.cod_aluno).first()
    academia = tb_academia.query.filter_by(cod_academia=aluno.cod_academia).first() 
    form = FormularioAgendaVisualizar()
    form.nome.data = aluno.nome_aluno
    form.academia.data = academia.nome_academia
    form.status.data = agenda.status_agenda
    form.horario.data = agenda.data_agenda.strftime('%d/%m/%Y %H:%M')
    return render_template('visualizarAgenda.html', titulo='Visualizar Agenda', id=id, form=form) 


#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarAgenda
#FUNÇÃO: visualizar informações da agenda no banco de dados
#PODE ACESSAR: personal
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarAgenda/<int:id>')
def editarAgenda(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarAluno')))  
    agenda = tb_agenda.query.filter_by(cod_agenda=id).first()
    aluno = tb_aluno.query.filter_by(cod_aluno=agenda.cod_aluno).first()
    academia = tb_academia.query.filter_by(cod_academia=aluno.cod_academia).first()     
    form = FormularioAgendaEdicao1()
    form.nome.data = aluno.nome_aluno
    form.academia.data = academia.nome_academia
    form.status.data = agenda.status_agenda
    #form.horario.data = agenda.data_agenda.strftime('%Y/%m/%d %H:%M:%S') 
    #form.horario.data = datetime.strptime(agenda.data_agenda, '%Y/%m/%d  %H:%M:%S')
    form.horario.data = agenda.data_agenda


    return render_template('editarAgenda.html', titulo='Editar Agenda', id=id, form=form)  

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarAgenda
#FUNÇÃO: alterar as informações da agenda no banco de dados
#PODE ACESSAR: personal
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarAgenda', methods=['POST','GET'])
def atualizarAgenda():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarAluno')))      
    form = FormularioAgendaEdicao1(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        agenda = tb_agenda.query.filter_by(cod_agenda=id).first()
        agenda.data_agenda = form.horario.data
        agenda.status_agenda = form.status.data
        db.session.add(agenda)
        db.session.commit()
        flash('Agenda atualizada com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarAgenda', id=request.form['id']))

##################################################################################################################################
#TIPO DE PAGAMENTOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: tipopagamento
#FUNÇÃO: tela do sistema para mostrar os tipos de pagamentos cadastrados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/tipopagamento', methods=['POST','GET'])
def tipopagamento():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('tipopagamento')))         
    page = request.args.get('page', 1, type=int)
    form = FormularPesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    
    if pesquisa == "" or pesquisa == None:     
        tipospagamento = tb_tipopagamento.query.order_by(tb_tipopagamento.desc_tipopagamento)\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        tipospagamento = tb_tipopagamento.query.order_by(tb_tipopagamento.desc_tipopagamento)\
        .filter(tb_tipopagamento.desc_tipopagamento.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('tipopagamento.html', titulo='Tipo Pagamento', tipospagamento=tipospagamento, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoTipoPagamento
#FUNÇÃO: mostrar o formulário de cadastro de tipo de pagamento
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoTipoPagamento')
def novoTipoPagamento():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoTipoPagamento'))) 
    form = FormularioTipoPagamentoEdicao()
    return render_template('novoTipoPagamento.html', titulo='Novo Tipo Pagamento', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarTipoPagamento
#FUNÇÃO: inserir informações do tipo de pagamento no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarTipoPagamento', methods=['POST',])
def criarTipoPagamento():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarTipoPaamento')))     
    form = FormularioTipoPagamentoEdicao(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarTipoPagamento'))
    desc  = form.descricao.data
    status = form.status.data
    tipopagamento = tb_tipopagamento.query.filter_by(desc_tipopagamento=desc).first()
    if tipopagamento:
        flash ('Tipo Pagamento já existe','danger')
        return redirect(url_for('tipopagamento')) 
    novoTipoPagamento = tb_tipopagamento(desc_tipopagamento=desc, status_tipopagamento=status)
    flash('Tipo de pagamento criado com sucesso!','success')
    db.session.add(novoTipoPagamento)
    db.session.commit()
    return redirect(url_for('tipopagamento'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarTipoPagamento
#FUNÇÃO: mostrar formulário de visualização dos tipos de pagamento cadastrados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarTipoPagamento/<int:id>')
def visualizarTipoPagamento(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarTipoPagamento')))  
    tipopagamento = tb_tipopagamento.query.filter_by(cod_tipopagamento=id).first()
    form = FormularioTipoPagamentoVisualizar()
    form.descricao.data = tipopagamento.desc_tipopagamento
    form.status.data = tipopagamento.status_tipopagamento
    return render_template('visualizarTipoPagamento.html', titulo='Visualizar Tipo Pagamento', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarTipoUsuario
##FUNÇÃO: mostrar formulário de edição dos tipos de usuários cadastrados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarTipoPagamento/<int:id>')
def editarTipoPagamento(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarTipoPagamento')))  
    tipopagamento = tb_tipopagamento.query.filter_by(cod_tipopagamento=id).first()
    form = FormularioTipoPagamentoEdicao()
    form.descricao.data = tipopagamento.desc_tipopagamento
    form.status.data = tipopagamento.status_tipopagamento
    return render_template('editarTipoPagamento.html', titulo='Editar Tipo Pagamento', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarTipoPagamento
#FUNÇÃO: alterar as informações dos tipos de usuários no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarTipoPagamento', methods=['POST',])
def atualizarTipoPagamento():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarTipoPagamento')))      
    form = FormularioTipoPagamentoEdicao(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        tipopagamento = tb_tipopagamento.query.filter_by(cod_tipopagamento=request.form['id']).first()
        tipopagamento.desc_tipopagamento = form.descricao.data
        tipopagamento.status_tipopagamento = form.status.data
        db.session.add(tipopagamento)
        db.session.commit()
        flash('Tipo de pagamento atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarTipoPagamento', id=request.form['id']))    

##################################################################################################################################
#RECEBIMENTO
##################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: recebimento
#FUNÇÃO: tela do sistema para mostrar o recebimento das mensalidades dos alunos
#PODE ACESSAR: somente o personal
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/recebimento', methods=['POST','GET'])
def recebimento():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('aluno')))         
    page = request.args.get('page', 1, type=int)
    form = FormularPesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    if pesquisa == "" or pesquisa == None:     
        recebimentos = tb_recebimento.query.order_by(tb_recebimento.dataprev_recebimento)\
        .join(tb_aluno, tb_aluno.cod_aluno==tb_recebimento.cod_aluno)\
        .join(tb_tipopagamento, tb_aluno.cod_tipopagamento==tb_tipopagamento.cod_tipopagamento)\
        .add_columns(tb_aluno.nome_aluno, tb_recebimento.dataprev_recebimento, tb_tipopagamento.desc_tipopagamento, tb_recebimento.cod_recebimento, tb_recebimento.status_recebimento)\
        .filter(tb_recebimento.cod_user == session['coduser_logado'])\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        recebimentos = tb_recebimento.query.order_by(tb_recebimento.dataprev_recebimento)\
        .join(tb_aluno, tb_aluno.cod_aluno==tb_recebimento.cod_aluno)\
        .join(tb_tipopagamento, tb_aluno.cod_tipopagamento==tb_tipopagamento.cod_tipopagamento)\
        .add_columns(tb_aluno.nome_aluno, tb_recebimento.dataprev_recebimento, tb_tipopagamento.desc_tipopagamento, tb_recebimento.cod_recebimento, tb_recebimento.status_recebimento)\
        .filter(tb_recebimento.cod_user == session['coduser_logado'])\
        .filter(tb_aluno.nome_aluno.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)   
    usuario = int(session['coduser_logado'])     
    return render_template('recebimento.html', titulo='Recebimento', recebimentos=recebimentos, form=form,usuario=usuario)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoRecebimento
#FUNÇÃO: mostrar o formulário de cadastro de recebimento
#PODE ACESSAR: usuários do tipo administrador e personal
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoRecebimento')
def novoRecebimento():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoAgenda'))) 
    form = FormularioRecebimentoEdicao()
    return render_template('novoRecebimento.html', titulo='Nova Recebimento', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarRecebimento
#FUNÇÃO: inserir informações de programação de recebimento no banco de dados
#PODE ACESSAR: área do sistema
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarRecebimento', methods=['POST',])
def criarRecebimento():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarAgenda')))     
    form = FormularioAgendaEdicao(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('novoAgenda'))
    datainicio = form.datainicio.data
    datafim = form.datafim.data
    if datainicio > datafim:
        flash('A data de inicio é maior que a data de fim ','danger')
        return redirect(url_for('novoAgenda')) 
    temAluno = tb_aluno.query.order_by(tb_aluno.nome_aluno)\
    .filter(tb_aluno.cod_user == session['coduser_logado'])\
    .filter(tb_aluno.status_aluno == 0)
    for aluno in temAluno:
        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days)):
                yield start_date + timedelta(n)
        start_date = (datainicio)
        end_date = (datafim)+ timedelta(days=1)
        for single_date in daterange(start_date, end_date):
            if int(aluno.diavenc_aluno) == (single_date.day):
                msg = msg + str(single_date.day) + "****"
                recebimento = tb_recebimento.query.order_by(tb_recebimento.dataprev_recebimento)\
                .filter(tb_recebimento.cod_aluno == aluno.cod_aluno)\
                .filter(tb_recebimento.dataprev_recebimento == single_date)\
                .filter(tb_recebimento.cod_user == session['coduser_logado'])
                rows = recebimento.count()  
                if rows == 0:
                    novoRecebimento= tb_recebimento(cod_user=session['coduser_logado'], cod_aluno=aluno.cod_aluno, dataprev_recebimento=single_date, status_recebimento=0)
                    db.session.add(novoRecebimento)
                    db.session.commit()                                                                                       
    return redirect(url_for('recebimento'))    

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarRecebimento
#FUNÇÃO: visualizar informações de recebimento de mensalidades no banco de dados
#PODE ACESSAR: personal
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarRecebimento/<int:id>')
def visualizarRecebimento(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarAgenda')))  
    recebimento = tb_recebimento.query.filter_by(cod_recebimento=id).first()
    aluno = tb_aluno.query.filter_by(cod_aluno=recebimento.cod_aluno).first()
    tipopagamento = tb_tipopagamento.query.filter_by(cod_tipopagamento=aluno.cod_tipopagamento).first() 
    form = FormularioRecebimentoVisualizar()
    form.nome.data = aluno.nome_aluno
    form.tipopagamento.data = tipopagamento.desc_tipopagamento
    form.status.data = recebimento.status_agenda
    form.horario.data = recebimento.dataprev_recebimento.strftime('%d/%m/%Y')
    return render_template('visualizarRecebimento.html', titulo='Visualizar Recebimento', id=id, form=form) 