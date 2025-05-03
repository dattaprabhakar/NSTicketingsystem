# app/extensions.py
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

mongo = PyMongo()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
mail = Mail()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'