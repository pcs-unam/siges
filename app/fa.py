# coding: utf-8
import datetime

from flask import Flask, url_for, redirect, render_template, request
from flask_admin.base import Admin, BaseView, expose
from flask_mongoengine import MongoEngine
from flask_admin.contrib.mongoengine import ModelView
from flask_mongoengine.wtf import model_form

# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'
app.config['MONGODB_SETTINGS'] = {'DB': 'posgrado'}

# Create models
db = MongoEngine()
db.init_app(app)


class Usuario(db.Document):
    email = db.EmailField(required=True)
    nombre = db.StringField(max_length=50)
    login = db.StringField(max_length=50)
    password = db.StringField(max_length=40)

    def get_id(self):
        return str(self.id)

    # Required for administrative interface
    def __unicode__(self):
        return self.login

    def __repr__(self):
        return "<usuario %s>" % self.login




class Anuncio(db.Document):
    usuario = db.ReferenceField(Usuario)
    descripcion = db.StringField(required=True)
    titulo = db.StringField(required=True)
    fecha = db.DateTimeField(required=False,
                                    default=datetime.datetime.now())
    def __unicode__(self):
        return self.titulo

    

if __name__ == '__main__':
#    init_login()

    # Create admin
    admin = Admin(app, 'Posgrado')

    # Add views
    admin.add_view(ModelView(Usuario))
    admin.add_view(ModelView(Anuncio))

    # Start app
    app.run(debug=True)
