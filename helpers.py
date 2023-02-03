#importações
import os
from personal import app, db
from models import tb_user, tb_usertype
from flask_wtf import FlaskForm
from wtforms import StringField, validators, SubmitField,IntegerField, SelectField,PasswordField,DateField,EmailField,BooleanField,RadioField


#criação via wftorm do formulario de usuarios
class FormularPesquisa(FlaskForm):
    pesquisa = StringField('Pesquisa:', [validators.Length(min=1, max=50)],render_kw={"placeholder": "digite sua pesquisa"} )
    pesquisa_responsiva = StringField('Pesquisa:', [validators.Length(min=1, max=50)],render_kw={"placeholder": "digite sua pesquisa"} )
    salvar = SubmitField('Pesquisar')

##------------------------------------------------------------------------------------------------------------------------------
# USUÁRIO
##------------------------------------------------------------------------------------------------------------------------------

#criação via wftorm do formulario de usuarios
class FormularioUsuario(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o nome do usuário"})
    status = SelectField('Situação:', coerce=int, choices=[(0,"Ativo"),(1,"Inativo")])
    login = StringField('Login:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o login do usuário"})    
    tipousuario = SelectField('Situação:', coerce=int,  choices=[(g.cod_usertype, g.desc_usertype) for g in tb_usertype.query.order_by('desc_usertype')])
    email = EmailField('Email:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o email do usuário"})
    salvar = SubmitField('Salvar')


#criação via wftorm do formulario de usuarios
class FormularioUsuarioVisualizar(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0,"Ativo"),(1,"Inativo")], render_kw={'readonly': True})
    login = StringField('Login:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    tipousuario = SelectField('Tipo:', coerce=int, choices=[(g.cod_usertype, g.desc_usertype) for g in tb_usertype.query.order_by('desc_usertype')], render_kw={'readonly': True})
    email = EmailField('Email:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    salvar = SubmitField('Editar')    

#criação via wftorm do formulario de usuarios
class FormularioUsuarioTrocarSenha(FlaskForm):
    senhaatual = PasswordField('Senha Atual:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a senha atual"})
    novasenha1 = PasswordField('Nova Senha:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a nova senha"})
    novasenha2 = PasswordField('Confirme Nova Senha:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite novamente a senha"})
    salvar = SubmitField('Editar')  

#------------------------------------------------------------------------------------------------------------------------------
#TIPO USUÁRIO
#------------------------------------------------------------------------------------------------------------------------------

#criação via wftorm do formulario de tipo usuarios
class FormularioTipoUsuarioEdicao(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a descrição do tipo de usuário"})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#criação via wftorm do formulario de tipo usuarios
class FormularioTipoUsuarioVisualizar(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')    

#------------------------------------------------------------------------------------------------------------------------------
#ACADEMIA
#------------------------------------------------------------------------------------------------------------------------------
#criação via wftorm do formulario de tipo usuarios
class FormularioAcademiaEdicao(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o nome da academia"})
    endereco = StringField('Endereço:', [validators.DataRequired(), validators.Length(min=1, max=90)], render_kw={"placeholder": "digite o endereço da academia"})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#criação via wftorm do formulario de tipo usuarios
class FormularioAcademiaVisualizar(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    endereco = StringField('Endereço:', [validators.DataRequired(), validators.Length(min=1, max=90)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')    