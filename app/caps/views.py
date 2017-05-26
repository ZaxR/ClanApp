import pandas as pd
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import desc

from app import db, models
from . import caps
from app.caps.forms import CapsForm

@caps.route('/addcaps', methods=['GET', 'POST'])
@login_required
def addcaps():
    form = CapsForm(request.form)

    if request.method == 'POST' and form.validate():
        from datetime import datetime
        new_cap = models.Caps(datetime.strftime(form.capdate.data, '%m/%d/%Y'),
                              capweek(form.capdate.data),
                              form.rsn.data,
                              form.captype.data)
        models.db.session.add(new_cap)
        models.db.session.commit()
        flash('Cap successfully added!')
        return redirect(url_for('caps.addcaps'))

    return render_template('caps/addcaps.html',
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


@caps.route('/viewcaps', methods=['GET', 'POST'])
@login_required
def viewcaps():
    df = pd.read_sql(models.Caps.query.statement, db.engine)
    capspivot = pd.crosstab(index=df.rsn, columns=df.week, values=df.captype,
                            aggfunc=max, dropna=True, margins=False).fillna('')
    capspivot = capspivot[capspivot.columns[::-1]]

    return render_template('caps/viewcaps.html', data=capspivot.to_html())
