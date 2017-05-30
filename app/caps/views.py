import pandas as pd
from datetime import datetime, date
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import desc

from app import db, models
from . import caps
from app.caps.forms import CapsForm

@caps.route('/caps', methods=['GET', 'POST'])
@login_required
def list_caps():
    captable = models.Caps.query.order_by(desc(models.Caps.id)).limit(10).all()

    return render_template('caps/caps.html', captable=captable, title="Caps")


@caps.route('/caps/add', methods=['GET', 'POST'])
@login_required
def add_cap():
    form = CapsForm(request.form)

    if request.method == 'POST' and form.validate():
        new_cap = models.Caps(datetime.strftime(form.capdate.data, '%m/%d/%Y'),
                              capweek(form.capdate.data),
                              form.rsn.data,
                              form.captype.data)

        try:
            # add department to the database
            db.session.add(new_cap)
            db.session.commit()
            flash('Cap successfully added.')
        except:
            flash('Something went wrong - please try again.')

        return redirect(url_for('caps.list_caps'))

    return render_template('caps/cap.html', action="caps.add_cap", form=form, title="Add Cap", button_text="Add")


@caps.route('/caps/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_cap(id):
    cap = models.Caps.query.get_or_404(id)
    form = CapsForm(obj=cap)
    if request.method == 'POST':  # form.validate_on_submit():
        cap.capdate = datetime.strftime(form.capdate.data, '%m/%d/%Y')
        cap.week = capweek(form.capdate.data)
        cap.name = form.rsn.data
        cap.captype = form.captype.data
        db.session.commit()
        flash('You have successfully edited the cap.')

        # redirect to the departments page
        return redirect(url_for('caps.list_caps'))

    form.capdate.data = datetime.strptime(cap.capdate, '%m/%d/%Y')
    form.rsn.data = cap.rsn
    form.captype.data = cap.captype
    return render_template('caps/cap.html', action="caps.edit_cap", id=id, form=form, title="Edit Cap", button_text="Save Changes")


@caps.route('/caps/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_cap(id):
    cap = models.Caps.query.get_or_404(id)
    db.session.delete(cap)
    db.session.commit()
    flash('You have successfully deleted the cap.')

    return redirect(url_for('caps.list_caps'))


@caps.route('/caps/add_week', methods=['GET', 'POST'])
@login_required
def add_cap_week():
    potential_cappers = models.Accounts.query.filter(models.Accounts.in_clan=="Yes").all()
    today = datetime.now().date()
    print(type(datetime.now().date()))

    for rsn in potential_cappers:
        new_cap = models.Caps(today.strftime('%m/%d/%Y'),
                              capweek(today),
                              rsn.rsn,
                              "No")
        db.session.add(new_cap)
    db.session.commit()

    flash('You have successfully added a week.')

    return redirect(url_for('caps.list_caps'))


def capweek(somedate, clanstart='2016-5-1'):
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
