import numpy as np
import pandas as pd
from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from flask_paginate import Pagination, get_page_args
from sqlalchemy import desc

from bokeh.charts import Bar, Line
from bokeh.embed import components
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.resources import INLINE

from app import db, models
from . import recruits
from app.recruits.forms import RecruitsForm


@recruits.route('/recruits', methods=['GET', 'POST'])
@login_required
def list_recruits():
    form = RecruitsForm(request.form)

    if request.method == 'POST' and form.validate():
        recruit_date = datetime.strftime(form.recruit_date.data, '%m/%d/%Y')
        new_recruit = models.Recruits(recruit_date,
                                      form.activity.data,
                                      form.recruiter.data,
                                      form.recruit.data,
                                      points(form.recruit.data, form.activity.data, recruit_date),
                                      change_to_recruit_count(form.activity.data))
        models.db.session.add(new_recruit)

        if form.activity.data == 'Join':
            new_account = models.Accounts(rsn=form.recruit.data, in_clan='Yes')
            models.db.session.add(new_account)
        else:
            account = models.Accounts.query.filter_by(rsn=form.recruit.data).first()
            account.in_clan = 'No'

        models.db.session.commit()
        flash('Recruit activity successfully added!')

        return redirect(url_for('recruits.list_recruits'))

    search = False
    q = request.args.get('q')
    if q:
        search = True

    page, per_page, offset = get_page_args()
    recruit_table = models.Recruits.query.order_by(desc(models.Recruits.id))
    recruit_table_render = recruit_table.limit(per_page).offset(offset)

    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=recruit_table.count(),search=search, record_name='recruit', css_framework='bootstrap3')

    return render_template('recruits/recruits.html', recruit_table=recruit_table_render, pagination=pagination, title="Caps", action="recruits.add_recruit", form=form)


@recruits.route('/recruits/add', methods=['GET', 'POST'])
@login_required
def add_recruit():
    form = RecruitsForm(request.form)

    if request.method == 'POST' and form.validate():
        recruit_date = datetime.strftime(form.recruit_date.data, '%m/%d/%Y')
        new_recruit = models.Recruits(recruit_date,
                                      form.activity.data,
                                      form.recruiter.data,
                                      form.recruit.data,
                                      points(form.recruit.data, form.activity.data, recruit_date),
                                      change_to_recruit_count(form.activity.data))
        models.db.session.add(new_recruit)

        if form.activity.data == 'Join':
            new_account = models.Accounts(rsn=form.recruit.data, in_clan='Yes')
            models.db.session.add(new_account)
        else:
            account = models.Accounts.query.filter_by(rsn=form.recruit.data).first()
            account.in_clan = 'No'

        models.db.session.commit()
        flash('Recruit activity successfully added!')

        return redirect(url_for('recruits.list_recruits'))

    return render_template('recruits/recruits.html', action="recruits.add_recruit", form=form, title="Add Recruit", button_text="Add")


@recruits.route('/recruits/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_recruit(id):
    recruit = models.Caps.query.get_or_404(id)
    form = RecruitsForm(obj=recruit)

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
        x = models.Recruits.query.filter_by(recruit=recruit).first()  # todo change to last, not first
        print(x.recruit_date)
        # todo change date and x.recruit_date to dates instead of strings
        days_in_clan = datetime.strptime(date, '%m/%d/%Y').date() - datetime.strptime(x.recruit_date, '%m/%d/%Y').date()
        print(days_in_clan)
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
    df = pd.read_sql(models.Recruits.query.statement, db.engine)

    # summary of recruiting by recruiter
    df['Total Recruits'] = df.groupby(['recruiter'])['change_to_recruit_count'].apply(lambda x: x == 1)
    df['Recruits Worth Points'] = df['points']
    df['Remaining Recruits'] = df['change_to_recruit_count']
    # also pull in_clan_or_not from Account ?

    retention_pivot = pd.pivot_table(df, index=["recruiter"],
                                     values=["Total Recruits", "Recruits Worth Points", "Remaining Recruits"],
                                     aggfunc=sum)

    retention_pivot['Retention Rate'] = retention_pivot['Remaining Recruits'] / retention_pivot['Total Recruits'] * 100
    # https://stackoverflow.com/questions/26313881/add-calculated-column-to-a-pandas-pivot-table

    # count by recruiter by day
    count_by_recruiter = pd.crosstab(index=df.recruit_date, columns=df.recruiter, values=df.change_to_recruit_count,
                                     aggfunc=sum, dropna=True, margins=False).fillna('')

    # cummulative count by recruiter over time; use for stacked bar chart
    df['cumulative'] = df.groupby(['recruiter'])['change_to_recruit_count'].cumsum()  # apply(lambda x: x.cumsum())
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
              title="Total Clan Members by Reccruiter Since Inception",
              responsive=True,
              tools='', tooltips=tooltips, toolbar_location=None,
              xlabel="Time", ylabel="Clan Size",
              legend='top_right')

    bar.xaxis.formatter = DatetimeTickFormatter(formats=dict(days=["%y"]))

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # Generate the script and HTML for the plot
    script, div = components(bar)

    return render_template('recruits/viewrecruits.html',
                           retention=retention_pivot.to_html(),
                           count=count_by_recruiter.to_html(),
                           cumsum=cumsum_by_recruiter.to_html(),
                           plot_script=script,
                           plot_div=div,
                           js_resources=js_resources,
                           css_resources=css_resources
                           )

# assign aggfuncs to values
# aggfunc = {"change_to_recruit_count": [np.mean, sum], "points?": sum})