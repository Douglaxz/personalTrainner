from personal import db

# criação da classe usuário conectada com o banco de dados mysql
class tb_user(db.Model):
    cod_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_user = db.Column(db.String(50), nullable=False)
    password_user = db.Column(db.String(50), nullable=False)
    status_user = db.Column(db.Integer, nullable=False)
    login_user = db.Column(db.String(50), nullable=False)
    cod_usertype = db.Column(db.Integer, nullable=False)
    email_user = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name

# criação da classe tipousuário conectada com o banco de dados mysql
class tb_usertype(db.Model):
    cod_usertype = db.Column(db.Integer, primary_key=True, autoincrement=True)
    desc_usertype = db.Column(db.String(50), nullable=False)
    status_usertype = db.Column(db.Integer, nullable=False)

# criação da classe tipousuário conectada com o banco de dados mysql
class tb_aluno(db.Model):
    cod_aluno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_aluno = db.Column(db.String(50), nullable=False)
    end_aluno = db.Column(db.String(90), nullable=False)
    datanasc_aluno = db.Column(db.DateTime, nullable=False)
    status_aluno = db.Column(db.Integer, nullable=False)
    cod_user = db.Column(db.Integer, nullable=False)
    cod_academia = db.Column(db.Integer, nullable=False)
    obs_aluno = db.Column(db.String(200), nullable=False)
    telefone_aluno = db.Column(db.String(50), nullable=False) 
    diavenc_aluno = db.Column(db.Integer, nullable=False)

class tb_academia(db.Model):
    cod_academia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_academia = db.Column(db.String(50), nullable=False)
    end_academia = db.Column(db.String(90), nullable=False)
    status_academia = db.Column(db.Integer, nullable=False)

