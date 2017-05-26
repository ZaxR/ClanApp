from flask import Flask, flash, redirect, request, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

csrf = CSRFProtect(app)
# todo Add csrf to non-form inputs and ajax
# todo Add csrf error_handler function and to templates
# todo give csrf its own secret key?

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# When True, the page the user is attempting to access is stored as next
# USE_SESSION_FOR_NEXT = True

from app import views, models
models.db.create_all()


# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return models.Users.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized_callback():
    # Used instead of login_manager.login_message = "You must be logged in to access this page."
    flash("You must be logged in to access this page.")
    return redirect(url_for('auth.login', next=request.endpoint))

# Register all blueprints
from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from .caps import caps as caps_blueprint
app.register_blueprint(caps_blueprint)

from .events import events as events_blueprint
app.register_blueprint(events_blueprint)

from .recruits import recruits as recruits_blueprint
app.register_blueprint(recruits_blueprint)

from .xp import xp as xp_blueprint
app.register_blueprint(xp_blueprint)
