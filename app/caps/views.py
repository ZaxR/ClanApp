import pandas as pd
from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from flask_paginate import Pagination, get_page_args
from sqlalchemy import desc, exists

from app import db, models
from . import caps
from app.caps.forms import CapsForm


@caps.route('/caps', methods=['GET', 'POST'])
@login_required
def list_caps():
    form = CapsForm(request.form)

    if request.method == 'POST':
        if db.session.query((exists().where(models.Caps.week == capweek(form.capdate.data)))).scalar():
            cap = models.Caps.query.filter_by(rsn=form.rsn.data).filter(models.Caps.week == capweek(form.capdate.data)).first()
            print(cap.id)
            return edit_cap(cap.id)
        else:
            join_date = [date.join_date for date in models.Accounts.query.filter(models.Accounts.rsn == form.rsn.data)]
            if capweek(form.capdate.data) < capweek(join_date[0]):
                flash("Player not yet in clan. Please select a date after {join_date}".format(join_date=join_date[0]))
            else:
                """if the capweek isn't before the join date, since every other week is automatically added, 
                it must be in the future"""
                flash("That date's in the future. Since I'm pretty sure you're not psychic, please try another date.")

            return redirect(url_for('caps.list_caps'))

    page, per_page, offset = get_page_args()
    cap_table = models.Caps.query.order_by(desc(models.Caps.id))
    cap_table_render = cap_table.limit(per_page).offset(offset)

    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=cap_table.count(),
                            record_name='cap', css_framework='bootstrap3')

    return render_template('caps/caps.html', captable=cap_table_render, pagination=pagination, title="Quick Update",
                           action="caps.list_caps", form=form)



def add_cap(form):  # Doesn't need to update "future" posts (like edit_cap()), because adding will only be done by cron scheduler for new week
    if form.validate():
        date = form.capdate.data
        week = capweek(form.capdate.data)
        rsn = form.rsn.data
        cap_type = form.captype.data
        caps_possible = possible_caps(form.rsn.data, date, "Add")
        count_caps = cap_count(form.rsn.data, date, form.captype.data, "Add")
        percentage_capped = cap_percentage(count_caps, caps_possible)
        streak = cap_streak(form.rsn.data, date, form.captype.data, "Add")
        recent_cap = last_cap(form.rsn.data, date, form.captype.data, "Add")

        new_cap = models.Caps(date, week, rsn, cap_type,
                              caps_possible, count_caps, percentage_capped, streak, recent_cap)

        try:
            db.session.add(new_cap)
            db.session.commit()
            flash('Cap successfully added.')
        except:
            flash('Something went wrong. Please try again.')

        return redirect(url_for('caps.list_caps'))

    else:
        flash('Fill the form completely and properly, dumb-dumb.')


@caps.route('/caps/edit/<int:cap_id>', methods=['GET', 'POST'])
@login_required
def edit_cap(cap_id):
    cap = models.Caps.query.get_or_404(cap_id)
    form = CapsForm(obj=cap)

    if request.method == 'POST':
        if form.validate():
            previous_capdate = cap.capdate

            cap.capdate = form.capdate.data
            cap.week = capweek(form.capdate.data)
            cap.name = form.rsn.data
            cap.captype = form.captype.data

            earlier_date = min(previous_capdate, cap.capdate)

            # Updates current cap and all future caps based on the cap's unchanged/new date
            entries = [cap for cap in models.Caps.query.filter_by(rsn=cap.name).
                       filter(models.Caps.capdate >= earlier_date).order_by(models.Caps.capdate)]

            for entry in entries:
                entry.possible_caps = possible_caps(entry.rsn, entry.capdate, "Edit")
                entry.cap_count = cap_count(entry.rsn, entry.capdate, entry.captype, "Edit")
                entry.cap_percentage = cap_percentage(entry.cap_count, entry.possible_caps)
                entry.cap_streak = cap_streak(entry.rsn, entry.capdate, entry.captype, "Edit")
                entry.last_cap = last_cap(entry.rsn, entry.capdate, entry.captype, "Edit")

                # previous_captype = entry.captype  # assumes going in order from past to present

            try:
                db.session.add(cap)
                db.session.commit()
                flash('You have successfully edited the cap.')
            except:
                flash('Something went wrong. Please try again.')

        else:
            flash('Fill the form completely and properly, dumb-dumb.')

        return redirect(url_for('caps.list_caps'))

    #form.capdate.data = datetime.strptime(cap.capdate, '%m/%d/%Y')  # needs to be at the bottom to format date properly

    return render_template('caps/cap.html', action="caps.edit_cap", cap_id=cap_id, form=form,
                           title="Edit Cap", button_text="Save Changes")


@caps.route('/caps/delete/<int:cap_id>', methods=['GET', 'POST'])
@login_required
def delete_cap(cap_id):
    try:
        cap = models.Caps.query.get_or_404(cap_id)
        db.session.delete(cap)
        db.session.commit()
        flash('You have successfully deleted the cap.')
    except:
        flash('Something went wrong - please try again.')

    return redirect(url_for('caps.list_caps'))


@caps.route('/caps/add_week', methods=['GET', 'POST'])
@login_required
def add_cap_week():
    potential_cappers = models.Accounts.query.filter(models.Accounts.in_clan == "Yes").all()
    today = datetime.now().date()

    for rsn in potential_cappers:
        date = today
        week = capweek(today)
        name = rsn.rsn
        cap_type = "No"
        caps_possible = possible_caps(name, date, "Add")
        count_caps = cap_count(name, date, cap_type, "Add")
        percentage_capped = cap_percentage(count_caps, caps_possible)
        streak = cap_streak(name, date, cap_type, "Add")
        recent_cap = last_cap(name, date, cap_type, "Add")

        new_cap = models.Caps(date, week, name, cap_type,
                              caps_possible, count_caps, percentage_capped, streak, recent_cap)
        db.session.add(new_cap)

    try:
        db.session.commit()
        flash('Successfully added caps for the week.')
    except:
        flash('Something went wrong. Please try again.')

    return redirect(url_for('caps.list_caps'))


def capweek(d1, clanstart='2016-5-1'):
    d0 = datetime.strptime(clanstart, '%Y-%m-%d').date()

    n, remainder = divmod((d1 - d0).days + 1, 7)
    if remainder > 0:
        n += 1

    return ("Wk " + str(n))


def possible_caps(rsn, date, form_type):
    # this will always work as is if cron scheduler for add week
    if form_type == "Add":
        return len(models.Caps.query.filter_by(rsn=rsn).filter(models.Caps.capdate <= date).all()) + 1
    return len(models.Caps.query.filter_by(rsn=rsn).filter(models.Caps.capdate <= date).all())


def cap_count(rsn, date, captype, form_type):
    cap_count = len(models.Caps.query.filter_by(rsn=rsn).
                    filter(models.Caps.capdate <= date).
                    filter(models.Caps.captype == "Yes").all())

    # Adds need to account for the new cap not yet being in the db; Edits are all included in the query already
    if form_type == "Add":
        if captype == "Yes":
            return cap_count + 1
    return cap_count


def cap_percentage(count, possible):
    return count / possible


def cap_streak(rsn, date, captype, form_type):
    from itertools import groupby

    cap_list = [c.captype for c in models.Caps.query.filter_by(rsn=rsn).
                order_by(models.Caps.capdate).filter(models.Caps.capdate <= date)]

    try:
        if form_type == "Add":
            cap_list.append(captype)
        return max(len(list(v)) for k, v in groupby(cap_list) if k == "Yes")
    except:
        return 0


def last_cap(rsn, date, captype, form_type):
    last = models.Caps.query.filter_by(rsn=rsn).\
        filter(models.Caps.captype == "Yes").\
        filter(models.Caps.capdate <= date).\
        order_by(desc(models.Caps.capdate)).first()

    if form_type == "Add":
        if captype == "Yes":
            return date
    try:
        return last.capdate
    except:
        return None


@caps.route('/viewcaps', methods=['GET', 'POST'])
@login_required
def viewcaps():
    df = pd.read_sql(models.Caps.query.statement, db.engine)

    df['edit_links'] = df.apply(lambda row: '<a href="http://localhost:4000/caps/edit/{0}">{1}</a>'.format(row['id'], row['captype']), axis=1)

    # Creates cap table view similar to Google Sheets version
    cap_summary = pd.crosstab(index=df.rsn, columns=df.week, values=df.edit_links,
                              aggfunc=max, dropna=True, margins=False).fillna('')
    cap_summary = cap_summary[natural_sort(cap_summary.columns)[::-1]]
    cap_summary.index.name = None
    cap_summary.columns.name = None


    # Summary of cap activity by RSN
    df2 = pd.read_sql(models.Caps.query.order_by(models.Caps.capdate).statement, db.engine)
    # todo need to sort by date and not id so 'last' pulls the right number
    cap_activity_pivot = pd.pivot_table(df2, index=["rsn"],
                                        values=["possible_caps", "cap_count",
                                                "cap_percentage", "cap_streak", "last_cap"],
                                        aggfunc='last')

    right_order = ["possible_caps", "cap_count", "cap_percentage", "cap_streak", "last_cap"]
    cap_activity_pivot = cap_activity_pivot.reindex(columns=right_order)
    cap_activity_pivot.index.name = None

    return render_template('caps/viewcaps.html',
                           cap_summary=cap_summary.to_html(classes='table', escape=False),
                           cap_activity=cap_activity_pivot.to_html())


def natural_sort(l):
    import re
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)