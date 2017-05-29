from flask import render_template
from flask_login import login_required

from app import app


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
