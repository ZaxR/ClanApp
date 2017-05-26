from flask import Flask, flash, redirect, request, session, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#When True, the page the user is attempting to access is stored as next
# USE_SESSION_FOR_NEXT = True

from app import views, models
models.db.create_all()

# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return models.Users.query.get(int(user_id))


@login_manager.unauthorized_handler
def handle_needs_login():
    # Used instead of login_manager.login_message = "You must be logged in to access this page."
    flash("You must be logged in to access this page.")
    return redirect(url_for('login', next=request.endpoint))
