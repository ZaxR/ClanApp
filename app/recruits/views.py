import numpy as np
import pandas as pd
from datetime import datetime, time
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from flask_paginate import Pagination, get_page_args
from sqlalchemy import and_, desc, exists

from bokeh.charts import Bar, Line, Step, TimeSeries
from bokeh.embed import components
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.resources import INLINE

from app import db, models
from . import recruits
from app.recruits.forms import RecruitsForm
from app.caps.views import add_cap


pd.set_option('display.max_colwidth', -1)


@recruits.route('/recruits', methods=['GET', 'POST'])
@login_required
def list_recruits():
    form = RecruitsForm(request.form)

    if request.method == 'POST':
        return add_recruit(form)

    page, per_page, offset = get_page_args()
    recruit_table = models.Recruits.query.order_by(desc(models.Recruits.id))
    recruit_table_render = recruit_table.limit(per_page).offset(offset)

    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=recruit_table.count(),
                            record_name='recruit', css_framework='bootstrap3')

    return render_template('recruits/recruits.html', recruit_table=recruit_table_render,
                           pagination=pagination, title="Recruits",
                           action="recruits.list_recruits", form=form)


def add_recruit(form):
    if form.validate():
        if form.activity.data == 'Join':
            # Makes sure there isn't already a clan member with the same name (prevents double entry).
            if db.session.query(exists().where(and_(models.Accounts.in_clan == 'Yes',
                                                    models.Accounts.rsn == form.recruit.data))).scalar():
                flash('Someone by that RSN is already in the clan.')
                return redirect(url_for('recruits.list_recruits'))

            # Make sure the date isn't in the future
            if form.recruit_date.data > datetime.now().date():
                flash("That date's in the future. Since I'm pretty sure you're not psychic, please try another date.")
                return redirect(url_for('recruits.list_recruits'))

            # Adds the recruit to the Accounts list
            new_account = models.Accounts(rsn=form.recruit.data, in_clan='Yes', join_date=form.recruit_date.data)
            models.db.session.add(new_account)

            # Adds a cap of "New" for the new recruit
            new_cap = add_cap(form.recruit_date.data, form.recruit.data, "New")
            models.db.session.add(new_cap)
        else:
            # This check will be made redundant when there's a dropdown of current members to select from for leaves
            if not db.session.query(exists().where(and_(models.Accounts.in_clan == 'Yes',
                                                        models.Accounts.rsn == form.recruit.data))).scalar():
                flash('There\'s no one currently in the clan with that RSN.')
                return redirect(url_for('recruits.list_recruits'))

            # Makes sure the leave date wasn't set before the person even joined the clan.
            join_date = [date.join_date for date in models.Accounts.query.filter(models.Accounts.rsn == form.recruit.data)]
            if form.recruit_date.data < join_date[0]:
                flash("Player was not yet in the clan. Please select a date on or after {join_date}".format(join_date=join_date[0]))
                return redirect(url_for('recruits.list_recruits'))

            # Make sure the date isn't in the future
            if form.recruit_date.data > datetime.now().date():
                flash("That date's in the future. Since I'm pretty sure you're not psychic, please try another date.")
                return redirect(url_for('recruits.list_recruits'))

            account = models.Accounts.query.filter_by(rsn=form.recruit.data).first()
            account.in_clan = 'No'
            account.leave_date = form.recruit_date.data

        # Adds the activity to the Recruits table
        new_recruit = models.Recruits(form.recruit_date.data,
                                      form.activity.data,
                                      form.recruiter.data,
                                      form.recruit.data,
                                      points(form.recruit.data, form.activity.data, form.recruit_date.data),
                                      change_to_recruit_count(form.activity.data))

        models.db.session.add(new_recruit)

        # Recalculate total recruiting points and add to Accounts.recruit_points
        # Just need to sum all in Recruits.points for the rsn and multiply by 10

        try:
            models.db.session.commit()
            flash('Recruit activity successfully added!')
        except:
            flash('Something went wrong. Please try again.')

    else:
        flash('Fill the form completely and properly, dumb-dumb.')

    return redirect(url_for('recruits.list_recruits'))


@recruits.route('/recruits/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_recruit(id):
    print(id, type(id))
    recruit = models.Recruits.query.get_or_404(id)
    form = RecruitsForm(obj=recruit)

    if request.method == 'POST':
        if form.validate():
            previous_recruit_date = recruit.recruit_date

            recruit.recruit_date = form.recruit_date.data
            recruit.activity_type = form.activity.data
            recruit.recruiter = form.recruiter.data
            recruit.recruit = form.recruit.data

            change_to_recruit_count(form.activity.data)

            earlier_date = min(previous_recruit_date, recruit.recruit_date)

            # Updates current recruit entry and all future entries
            entries = [recruit for recruit in models.Recruits.query.filter_by(recruiter=recruit.recruiter).
                       filter(models.Recruits.recruit_date >= earlier_date).order_by(models.Recruits.recruit_date)]

            for entry in entries:
                entry.points = points(entry.recruit, entry.activity_type, entry.recruit_date)  # "Edit"

            try:
                db.session.add(recruit)
                db.session.commit()
                flash('You have successfully edited the recruiting entry.')
            except:
                flash('Something went wrong. Please try again.')

        else:
            flash('Fill the form completely and properly, dumb-dumb.')

        return redirect(url_for('recruits.list_recruits'))

    return render_template('recruits/recruit.html', action="recruits.edit_recruit", id=id, form=form,
                           title="Edit Recruit", button_text="Save Changes")


@recruits.route('/recruits/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_recruit(id):
    recruit = models.Recruits.query.get_or_404(id)
    db.session.delete(recruit)
    db.session.commit()
    flash('You have successfully deleted the recruit.')

    return redirect(url_for('recruits.list_recruits'))


def points(recruit, type, date):
    """Point awarded for joins, but taken away if the recruit leaves within 7 days"""
    if type == "Join":
        return 1
    else:
        x = models.Recruits.query.filter_by(recruit=recruit).order_by(desc(models.Recruits.id)).first()
        # todo change date and x.recruit_date to dates instead of strings
        days_in_clan = date - x.recruit_date
        if days_in_clan.days >= 7:
            return 0
        return -1


def change_to_recruit_count(type):
    if type == "Join":
        return 1
    return -1


@recruits.route('/viewrecruits', methods=['GET', 'POST'])
@login_required
def viewrecruits():
    df = pd.read_sql(models.Recruits.query.order_by(models.Recruits.recruit_date).statement, db.engine)

    # summary of recruiting by recruiter
    df['Total Recruits'] = df.groupby(['recruiter'])['change_to_recruit_count'].apply(lambda x: x == 1)
    df['Recruits Worth Points'] = df['points']
    df['Remaining Recruits'] = df['change_to_recruit_count']
    # also pull in_clan_or_not from Account ?

    retention_pivot = pd.pivot_table(df, index=["recruiter"],
                                     values=["Total Recruits", "Recruits Worth Points", "Remaining Recruits"],
                                     aggfunc=sum)

    retention_pivot['Retention Rate'] = retention_pivot['Remaining Recruits'] / retention_pivot['Total Recruits']
    right_order = ["Total Recruits", "Recruits Worth Points", "Remaining Recruits", "Retention Rate"]
    retention_pivot = retention_pivot.reindex(columns=right_order)
    retention_pivot.index.name = None

    # count by recruiter by day
    count_by_recruiter = pd.crosstab(index=df.recruit_date, columns=df.recruiter, values=df.change_to_recruit_count,
                                     aggfunc=sum, dropna=True, margins=False).fillna('')

    # cummulative count by recruiter over time; use for stacked bar chart
    df['cumulative'] = df.groupby(['recruiter'])['change_to_recruit_count'].cumsum()
    cumsum_by_recruiter = pd.pivot_table(df, index="recruit_date", columns='recruiter', values='cumulative',
                                         aggfunc=sum, dropna=True, margins=False).fillna(method='pad').fillna('')

    cumsum_stacked = cumsum_by_recruiter.stack().rename_axis(['recruit_date', 'recruiter']).reset_index(name='value')\
        .fillna(method='pad').fillna('')
    cumsum_stacked["value"] = pd.to_numeric(cumsum_stacked["value"])

    tooltips = [
        ('Recruiter', '@recruiter'),
        ('Recruits', '@value')
    ]

    bar = Bar(cumsum_stacked,
              label='recruit_date', values='value', stack='recruiter', agg='sum',
              responsive=True,
              tools='', tooltips=tooltips, toolbar_location=None,
              xlabel="Date", ylabel="Clan Size",
              legend='top_left')

    # bar.xaxis.formatter = DatetimeTickFormatter(months=["%m"], days=["%d"], years=["%Y"])

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # Generate the script and HTML for the plot
    bar_script, bar_div = components(bar)

    return render_template('recruits/viewrecruits.html',
                           retention=retention_pivot.to_html(classes='table table-hover table-condensed',
                                                             formatters={'Retention Rate': '{:,.0%}'.format}),
                           count=count_by_recruiter.to_html(),
                           cumsum=cumsum_by_recruiter.to_html(),
                           bar_script=bar_script,
                           bar_div=bar_div,
                           js_resources=js_resources,
                           css_resources=css_resources)
