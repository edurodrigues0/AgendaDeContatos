import os
from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qweasdzxc123098'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)

class Contacts(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100))
  email = db.Column(db.String())
  phone = db.Column(db.String())
  image = db.Column(db.String())
  user_id = db.Column(
    db.Integer,
    db.ForeignKey('user.id')
  )
  created_at = db.Column(db.String)
  update_at = db.Column(db.String)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String())
  email = db.Column(db.String())
  password = db.Column(db.String())
  created_at = db.Column(db.String)
  updated_at = db.Column(db.String)

@app.route('/')
def index():
  if 'user_id' not in session:
    return redirect('/login')

  contact = Contacts.query.filter_by(
    user_id=session['user_id']
  ).all()

  return render_template(
    'index.html',
    contacts=contact
  )

@app.route('/create', methods=['POST'])
def create():
  name = request.form.get('name')
  email = request.form.get('email')
  phone = request.form.get('phone')
  new_contact = Contacts(
    name=name,
    email=email,
    phone=phone,
    user_id=session['user_id']
  )
  db.session.add(new_contact)
  db.session.commit()

  flash('Contato criado com sucesso!', 'success')
  return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
  contact = Contacts.query.filter_by(id=id).first()
  db.session.delete(contact)
  db.session.commit()

  flash('Contato deletado com sucesso!', 'success')
  return redirect('/')

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
  name = request.form.get('name')
  email = request.form.get('email')
  phone = request.form.get('phone')
  contact = Contacts.query.filter_by(id=id).first()
  
  contact.name = name
  contact.email = email
  contact.phone = phone
  db.session.commit()

  flash('Contato editado com suucesso!', 'success')
  return redirect('/')

@app.route('/login')
def login():
  return render_template('login.html')

@app.route('/register')
def register():
  return render_template('register.html')

@app.route('/signin', methods=['POST'])
def signin():
  email = request.form.get('email')
  password = request.form.get('password')

  user = User.query.filter_by(email=email).first()
  
  if not user:
    flash('Usuário não encontrado!', 'error')
    return redirect('/login')

  if not check_password_hash(user.password, password):
    flash('Senha incorreta!', 'error')
    return redirect('/login')

  flash(f'Bem vindo, {user.name}', 'success')
  session['user_id'] = user.id
  return redirect('/')

@app.route('/signup', methods=['POST'])
def signup():
  name = request.form.get('name')
  email = request.form.get('email')
  password = request.form.get('password')

  user = User.query.filter_by(email=email).first()
  if user:
    flash('E-mail já existe no sistema!', 'error')
    return redirect('/register')

  new_user = User(
    name=name,
    email=email,
    password=generate_password_hash(
      password,
      method='sha256'
    )
  )
  db.session.add(new_user)
  db.session.commit()

  flash('Usuário criado com sucesso!', 'success')
  return redirect('/login')

@app.route('/logout')
def logout():
  session.pop('user_id', None)
  flash('Logout com sucesso!', 'success')
  return redirect('/login')

if __name__ == '__main__':
  db.create_all()

  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0',port=port)
