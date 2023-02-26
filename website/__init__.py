from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# __init__ creates a python package out of this notebook.
db = SQLAlchemy()
DB_NAME = "CPDB.db"

# code that only creates the app once the function and the package are run
def create_app():
    CP = Flask(__name__)
    CP.config["SECRET_KEY"] = "aorjfn awoibaf"
    
    CP.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    CP.config["SQLALCHEMY_TRACE_MODIFICATIONS"] = True

    # create the database and link it to the app CP
    db.init_app(CP)

    # import the Python page viewers and endpoints
    # auth = authentication pages, views = everything else, models = DB models
    
    from .views import views
    from .auth import auth
    from . import models

    CP.register_blueprint(views, url_prefix="/")
    CP.register_blueprint(auth, url_prefix="/")
    
    with CP.app_context():
        db.create_all()

    login_manager = LoginManager()

    # where must the user go if they are NOT logged in when login required
    login_manager.login_view = "auth.login"
    login_manager.init_app(CP)

    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    return CP
