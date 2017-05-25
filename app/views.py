from flask import flash, jsonify, redirect, render_template, request, session, url_for, abort
from flask_login import logout_user, login_required, login_manager, login_user
from app import app, db, models, forms
from sqlalchemy import desc
import json


@app.route('/')
@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = models.Users.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid e-mail or password')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You have successfully been logged out.')
    return redirect(url_for('index'))


@app.route('/addcaps', methods=['GET', 'POST'])
def addcaps():
    form = forms.CapsForm(request.form)

    if not session.get('logged_in'):
        return redirect(url_for('index'))

    if request.method == 'POST':  # and form.validate()
        from datetime import datetime
        new_cap = models.Caps(datetime.strftime(form.capdate.data, '%m/%d/%Y'),
                              capweek(form.capdate.data),
                              form.rsn.data,
                              form.captype.data)
        models.db.session.add(new_cap)
        models.db.session.commit()
        flash('Cap successfully added!')
        return redirect(url_for('addcaps'))

    return render_template('addcaps.html',
                           captable=models.Caps.query.order_by(desc(models.Caps.id)).limit(10).all(), form=form)


def capweek(somedate, clanstart='2016-5-1'):
    from datetime import datetime
    try:
        d1 = somedate
    except:
        d1 = datetime.now().date()

    d0 = datetime.strptime(clanstart, '%Y-%m-%d').date()
    n, remainder = divmod((d1 - d0).days + 1, 7)
    if remainder > 0:
        n += 1

    return ("Wk " + str(n))


@app.route('/viewcaps', methods=['GET', 'POST'])
def viewcaps():
    from pandas import crosstab
    import pandas as pd
    import numpy as np

    df = pd.read_sql(models.Caps.query.statement, db.engine)
    capspivot = crosstab(index=df.rsn, columns=df.week[::-1], values=df.captype,
                         aggfunc=max, dropna=True, margins=False).fillna('')

    return render_template('viewcaps.html', data=capspivot.to_html())
