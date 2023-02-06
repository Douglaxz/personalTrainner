#importações
import os
from personal import app, db
from models import tb_user, tb_usertype, tb_academia, tb_aluno, tb_tipopagamento
from flask_wtf import FlaskForm
from wtforms import Form, StringField, validators, SubmitField,IntegerField, SelectField,PasswordField,DateField,EmailField,BooleanField,RadioField, TextAreaField, TimeField, TelField, DateTimeLocalField

##################################################################################################################################
#PESQUISA
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: pesquisa (geral)
#TIPO: edição
#TABELA: nenhuma
#---------------------------------------------------------------------------------------------------------------------------------
class FormularPesquisa(FlaskForm):
    pesquisa = StringField('Pesquisa:', [validators.Length(min=1, max=50)],render_kw={"placeholder": "digite sua pesquisa"} )
    pesquisa_responsiva = StringField('Pesquisa:', [validators.Length(min=1, max=50)],render_kw={"placeholder": "digite sua pesquisa"} )
    salvar = SubmitField('Pesquisar')

##################################################################################################################################
#USUÁRIO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: usuários
#TIPO: edição
#TABELA: tb_user
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioUsuario(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o nome do usuário"})
    status = SelectField('Situação:', coerce=int, choices=[(0,"Ativo"),(1,"Inativo")])
    login = StringField('Login:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o login do usuário"})    
    tipousuario = SelectField('Situação:', coerce=int,  choices=[(g.cod_usertype, g.desc_usertype) for g in tb_usertype.query.order_by('desc_usertype')])
    email = EmailField('Email:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o email do usuário"})
    salvar = SubmitField('Salvar')


#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: usuários
#TIPO: visualização
#TABELA: tb_user
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioUsuarioVisualizar(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0,"Ativo"),(1,"Inativo")], render_kw={'readonly': True})
    login = StringField('Login:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    tipousuario = SelectField('Tipo:', coerce=int, choices=[(g.cod_usertype, g.desc_usertype) for g in tb_usertype.query.order_by('desc_usertype')], render_kw={'readonly': True})
    email = EmailField('Email:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    salvar = SubmitField('Editar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: trocar senha do usuário
#TIPO: edição
#TABELA: tb_user
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioUsuarioTrocarSenha(FlaskForm):
    senhaatual = PasswordField('Senha Atual:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a senha atual"})
    novasenha1 = PasswordField('Nova Senha:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a nova senha"})
    novasenha2 = PasswordField('Confirme Nova Senha:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite novamente a senha"})
    salvar = SubmitField('Editar')  

##################################################################################################################################
#TIPO DE USUÁRIO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de usuário
#TIPO: edição
#TABELA: tb_usertype
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioTipoUsuarioEdicao(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a descrição do tipo de usuário"})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de usuário
#TIPO: visualização
#TABELA: tb_usertype
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioTipoUsuarioVisualizar(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')    

##################################################################################################################################
#ACADEMIA
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: academia
#TIPO: edição
#TABELA: tb_academia
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioAcademiaEdicao(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o nome da academia"})
    endereco = StringField('Endereço:', [validators.DataRequired(), validators.Length(min=1, max=90)], render_kw={"placeholder": "digite o endereço da academia"})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: academia
#TIPO: visualização
#TABELA: tb_academia
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioAcademiaVisualizar(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    endereco = StringField('Endereço:', [validators.DataRequired(), validators.Length(min=1, max=90)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')    

##################################################################################################################################
#ALUNOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: aluno
#TIPO: edição
#TABELA: tb_aluno
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioAlunoEdicao(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o nome do aluno"})
    endereco = StringField('Endereço:', [validators.DataRequired(), validators.Length(min=1, max=100)],render_kw={"placeholder": "digite o endereço do aluno"})
    datanascimento = DateField('Data de Nascimento:', [validators.DataRequired()],render_kw={"placeholder": "digite a data de nascimento do aluno"})
    status = SelectField('Situação:', coerce=int, choices=[(0,"Ativo"),(1,"Inativo")])
    observacoes = TextAreaField('Observações:', [validators.DataRequired(), validators.Length(min=1, max=500)],render_kw={"placeholder": "digite as observações do aluno"})    
    academia = SelectField('Academia:', coerce=int,  choices=[(g.cod_academia, g.nome_academia) for g in tb_academia.query.order_by('nome_academia')])
    telefone = StringField('Telefone:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o telefone do aluno"})
    diavencimento = IntegerField('Dia de Vencimento:', [validators.DataRequired()],render_kw={"placeholder": "digite o dia de vencimento do aluno"})
    horarioinicio = TimeField('Horário Inicio:', [validators.DataRequired()],render_kw={"placeholder": "digite o horario de inicio do aluno"})
    horariofinal = TimeField('Horário Fim:', [validators.DataRequired()],render_kw={"placeholder": "digite o horario fim do aluno"})
    diadom = BooleanField('Domingo:')
    diaseg = BooleanField('Segunda:')
    diater = BooleanField('Terça:')
    diaqua = BooleanField('Quarta:')
    diaqui = BooleanField('Quinta:')
    diasex = BooleanField('Sexta:')
    diasab = BooleanField('Sábado:')
    salvar = SubmitField('Salvar')
    tipopagamento = SelectField('Forma pagamento:', coerce=int,  choices=[(g.cod_tipopagamento, g.desc_tipopagamento) for g in tb_tipopagamento.query.order_by('desc_tipopagamento')])


#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: aluno
#TIPO: visualização
#TABELA: tb_alunos
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioAlunoVisualizar(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={'readonly': True})
    endereco = StringField('Endereço:', [validators.DataRequired(), validators.Length(min=1, max=100)],render_kw={'readonly': True})
    datanascimento = StringField('Data de Nascimento:', [validators.DataRequired()],render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0,"Ativo"),(1,"Inativo")], render_kw={'readonly': True})
    observacoes = TextAreaField('Observações:', [validators.DataRequired(), validators.Length(min=1, max=500)], render_kw={'readonly': True})
    academia = SelectField('Academia:', coerce=int, choices=[(g.cod_academia, g.nome_academia) for g in tb_academia.query.order_by('nome_academia')], render_kw={'readonly': True})
    telefone = StringField('Telefone:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    diavencimento = IntegerField('Dia de Vencimento:', [validators.DataRequired()], render_kw={'readonly': True})
    horarioinicio = TimeField('Horário:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={'readonly': True})
    horariofinal = TimeField('Horário:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    diadom = BooleanField('Domingo:', render_kw={'readonly': True})
    diaseg = BooleanField('Segunda:', render_kw={'readonly': True})
    diater = BooleanField('Terça:', render_kw={'readonly': True})
    diaqua = BooleanField('Quarta:', render_kw={'readonly': True})
    diaqui = BooleanField('Quinta:', render_kw={'readonly': True})
    diasex = BooleanField('Sexta:', render_kw={'readonly': True})
    diasab = BooleanField('Sábado:', render_kw={'readonly': True})    
    salvar = SubmitField('Editar', render_kw={'readonly': True})
    tipopagamento = SelectField('Forma pagamento:', coerce=int,  choices=[(g.cod_tipopagamento, g.desc_tipopagamento) for g in tb_tipopagamento.query.order_by('desc_tipopagamento')],render_kw={'readonly': True})

##################################################################################################################################
#AGENDA
##################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: agenda criação
#TIPO: edição
#TABELA: tb_agenda
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioAgendaEdicao(FlaskForm):
    datainicio = DateField('Data Inicio:', [validators.DataRequired()],render_kw={"placeholder": "digite a data de inicio do agendamento"})
    datafim = DateField('Data Fim:', [validators.DataRequired()],render_kw={"placeholder": "digite a data final do agendamento"})
    salvar = SubmitField('Salvar')   

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: visualizar agenda
#TIPO: visualização
#TABELA: tb_agenda
#--------------------------------------------------------------------------------------------------------------------------------- 
class FormularioAgendaVisualizar(FlaskForm):
    horario = StringField('Horário:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={'readonly': True})
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=100)],render_kw={'readonly': True})
    academia = StringField('Academia:', [validators.DataRequired(), validators.Length(min=1, max=100)],render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0,"Agendada"),(1,"Realizada"),(2,"Cancelada - Faltou"),(3,"Cancelada - Reposição")], render_kw={'readonly': True})

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: editar agenda
#TIPO: edição
#TABELA: tb_agenda
#--------------------------------------------------------------------------------------------------------------------------------- 
class FormularioAgendaEdicao1(FlaskForm):
    horario = DateTimeLocalField('Horário:', [validators.DataRequired()], format='%Y-%m-%dT%H:%M')
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=100)],render_kw={'readonly': True})
    academia = StringField('Academia:', [validators.DataRequired(), validators.Length(min=1, max=100)],render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0,"Agendada"),(1,"Realizada"),(2,"Cancelada - Faltou"),(3,"Cancelada - Reposição")])


#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: editar agenda não programada
#TIPO: edição
#TABELA: tb_agenda
#--------------------------------------------------------------------------------------------------------------------------------- 
class FormularioAgendaEdicao2(FlaskForm):
    horario = DateTimeLocalField('Horário:', [validators.DataRequired()], format='%Y-%m-%dT%H:%M')
    aluno =SelectField('Aluno:', choices=[])

##################################################################################################################################
#TIPO DE PAGAMENTO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de pagamento
#TIPO: edição
#TABELA: tb_pagamento
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioTipoPagamentoEdicao(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a descrição do tipo de usuário"})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de pagamento
#TIPO: visualização
#TABELA: tb_pagamento
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioTipoPagamentoVisualizar(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')    