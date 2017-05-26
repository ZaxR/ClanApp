from flask import Blueprint


xp = Blueprint('xp', __name__)

from . import views