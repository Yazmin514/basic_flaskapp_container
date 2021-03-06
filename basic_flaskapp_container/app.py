import datetime
import uuid
import os

from flask import Flask, render_template, redirect, url_for, session, flash

from flask_session import Session

from pymongo import MongoClient
from redis import Redis

from forms import *

mongo = MongoClient("mongodb://bdd_mongo:27017/")
mongodb = mongo.testdb

redis = Redis(host="bdd_redis")

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis

Session(app)

@app.route("/", methods=["GET", "POST"])
def timeline():
    user = session.get('profile')
    if not user:
        return redirect(url_for('login'))

    form = Fpublicacion()

    if form.validate_on_submit():
        post = {
            'publicacion': form.publicacion.data,
            'user_id': user['_id']
        }
        mongodb.posts.insert_one(post)
        return redirect(url_for('timeline'))

    posts = list(mongodb.posts.find())
    for post in posts:
        post['user']= mongodb.users.find_one({'_id' : post['user_id']})

    
    #return str(user)
    return render_template('home.html', form=form, user=user, posts=posts)

@app.route("/logout")
def logout():
    session['profile'] = None
    return redirect(url_for('timeline'))

@app.route("/signup", methods=["GET","POST"])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        user = {
            'name': form.name.data,
            'apellidos': form.apellidos.data,
            'biografia': form.biografia.data,
            'correo': form.correo.data,
            'telefono': form.telefono.data,
            'password': form.password.data
        }
        mongodb.users.insert_one(user)
        return redirect(url_for("login"))
        #return str(user)
    return render_template("signup.html", form=form)
    #return "Registrarse al Sistema"

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginFrom()
    if form.validate_on_submit():
        user = mongodb.users.find_one({
            'name': form.name.data,
            'password': form.password.data
        })

        if not user:
            flash('Usuario Incorrecto')
            return redirect(url_for('login'))
            #return "Credenciales Invalidas"

        session['profile'] = user
        return redirect(url_for('timeline'))
        #else:
            #return "Acceso Correcto"
        #mongodb.users.insert_one(user)
        #return str(user)
    #return "Iniciar Sesion"
    return render_template("login.html", form=form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5090, debug=True)
