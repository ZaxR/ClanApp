from datetime import datetime

import pandas as pd
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import desc

from app import db, models
from app.caps.forms import CapsForm
from . import caps

pd.set_option('display.max_colwidth', -1)


@caps.route('/caps', methods=['GET', 'POST'])
@login_required
def list_caps():
    # Creates cap table view similar to Google Sheets version
    df = pd.read_sql(models.Caps.query.statement, db.engine)
    df['edit_links'] = df.apply(lambda row: '<a href="/caps/edit/{0}">'
                                            '{1}<i class="fa fa-pencil"></i></a>'.
                                            format(row['id'], row['captype']), axis=1)

    cap_summary = pd.crosstab(index=df.rsn, columns=df.week, values=df.edit_links,
                              aggfunc=max, dropna=True, margins=False).fillna('')
    cap_summary = cap_summary[natural_sort(cap_summary.columns)[::-1]]
    cap_summary.index.name = None
    cap_summary.columns.name = None

    return render_template('caps/caps.html', action="caps.list_caps",
                           cap_summary=cap_summary.to_html(classes='table table-hover table-condensed table-fixed', escape=False))


@caps.route('/caps/edit/<int:cap_id>', methods=['GET', 'POST'])
@login_required
def edit_cap(cap_id):
    cap = models.Caps.query.get_or_404(cap_id)
    form = CapsForm(obj=cap)

    if request.method == 'POST':
        if form.validate():
            if cap.week != capweek(form.capdate.data):
                flash('Please select a date that falls within the selected cap week or edit a different record.')
                return redirect(url_for('caps.edit_cap', cap_id=cap_id))

            join_date = [date.join_date for date in models.Accounts.query.filter(models.Accounts.rsn == cap.rsn)]
            if form.capdate.data < join_date[0]:
                flash("Player not yet in clan. Please select a date on or after {join_date}".format(join_date=join_date[0]))
                return redirect(url_for('caps.edit_cap', cap_id=cap_id))

            if form.capdate.data > datetime.now().date():
                flash("That date's in the future. Since I'm pretty sure you're not psychic, please try another date.")
                return redirect(url_for('caps.edit_cap', cap_id=cap_id))

            previous_capdate = cap.capdate

            cap.capdate = form.capdate.data
            cap.week = capweek(form.capdate.data)
            cap.name = form.rsn.data
            cap.captype = form.captype.data

            earlier_date = min(previous_capdate, cap.capdate)

            # Updates current cap and all caps after that date based on the earlier of the previous/new date
            entries = [cap for cap in models.Caps.query.filter_by(rsn=cap.name).
                       filter(models.Caps.capdate >= earlier_date).order_by(models.Caps.capdate)]

            for entry in entries:
                entry.possible_caps = possible_caps(entry.rsn, entry.capdate, "Edit")
                entry.cap_count = cap_count(entry.rsn, entry.capdate, entry.captype, "Edit")
                entry.cap_percentage = cap_percentage(entry.cap_count, entry.possible_caps)
                entry.cap_streak = cap_streak(entry.rsn, entry.capdate, entry.captype, "Edit")
                entry.last_cap = last_cap(entry.rsn, entry.capdate, entry.captype, "Edit")

            try:
                db.session.add(cap)
                db.session.commit()

                # Update caps for rank sheet
                q = models.Caps.query.filter_by(rsn=cap.rsn).order_by(desc(models.Caps.capdate)).first()
                a = models.Accounts.query.filter(models.Accounts.rsn == cap.rsn).first()
                a.cap_points = q.cap_count
                db.session.commit()

                flash('You have successfully edited the cap.')
            except:
                flash('Something went wrong. Please try again.')

        else:
            flash('Fill the form completely and properly, dumb-dumb.')

        return redirect(url_for('caps.list_caps'))

    return render_template('caps/cap.html', action="caps.edit_cap", cap_id=cap_id, form=form,
                           title="Edit Cap", button_text="Save Changes", rsn=cap.rsn)


# Not currently used. Could be added to an admin panel
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


# Only used by cron scheduled add_cap_week and on new recruit
def add_cap(date, rsn, cap_type):
    week = capweek(date)
    caps_possible = possible_caps(rsn, date, "Add")
    count_caps = cap_count(rsn, date, cap_type, "Add")
    percentage_capped = cap_percentage(count_caps, caps_possible)
    streak = cap_streak(rsn, date, cap_type, "Add")
    recent_cap = last_cap(rsn, date, cap_type, "Add")

    return models.Caps(date, week, rsn, cap_type,
                       caps_possible, count_caps, percentage_capped, streak, recent_cap)


@caps.route('/caps/add_week', methods=['GET', 'POST'])
@login_required
def add_cap_week():
    potential_cappers = models.Accounts.query.filter(models.Accounts.in_clan == "Yes").all()
    today = datetime.now().date()

    for rsn in potential_cappers:
        new_cap = add_cap(today, rsn.rsn, "No")
        db.session.add(new_cap)

    try:
        db.session.commit()
        flash('Successfully added caps for the week.')
    except:
        flash('Something went wrong. Please try again.')

    return redirect(url_for('caps.list_caps'))


def capweek(d1, clanstart='2016-5-3'):
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
    # Summary of cap activity by RSN
    df2 = pd.read_sql(models.Caps.query.order_by(models.Caps.capdate).statement, db.engine)
    df2 = df2.rename(columns={"possible_caps":"Possible", "cap_count":"Total", "cap_percentage": "%",
                        "cap_streak":"Streak", "last_cap":"Last"})

    cap_activity_pivot = pd.pivot_table(df2, index=["rsn"], values=["Possible", "Total", "%", "Streak", "Last"],
                                        aggfunc='last')

    cap_activity_pivot = cap_activity_pivot.reindex(columns=["Possible", "Total", "%", "Streak", "Last"])
    cap_activity_pivot.index.name = None

    return render_template('caps/viewcaps.html',
                           cap_activity=cap_activity_pivot.to_html(classes='table table-hover table-condensed',
                                                                   formatters={'%': '{:,.0%}'.format}))

def natural_sort(l):
    import re
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)


# line = TimeSeries(df.change_to_recruit_count, xlabel='Date', ylabel='Clan Size')
# line_script, line_div = components(line)