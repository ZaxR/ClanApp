from flask import flash, redirect, render_template, request, url_for
from flask_login import logout_user, login_required, login_user

from app import models
from app.auth.forms import LoginForm
from . import auth


@auth.route('/login', methods=['GET', 'POST'])
def login():  # todo known issues: needs flask.abort and 400 page for improper redirect attempts; werkzeug.exceptions.abort?
# todo don't allow logged in users to go to the login page
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = models.Users.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for(request.args.get('next') or 'index'))
        else:
            flash('Invalid e-mail or password')
    return render_template('auth/login.html', next=request.args.get('next'), form=form, title='Login')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully been logged out.')
    return redirect(url_for('auth.login'))