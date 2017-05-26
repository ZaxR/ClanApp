from flask import Blueprint


caps = Blueprint('caps', __name__)

from . import views