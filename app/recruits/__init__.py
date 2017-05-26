from flask import Blueprint


recruits = Blueprint('recruits', __name__)

from . import views