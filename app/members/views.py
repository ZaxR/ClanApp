import pandas as pd
from flask import render_template
from flask_login import login_required

from app import db, models
from app.caps.views import natural_sort
from . import members


@members.route('/ranksheet', methods=['GET', 'POST'])
@login_required
def ranksheet():
    # Creates rank sheet
    df = pd.read_sql(models.Accounts.query.filter(models.Accounts.in_clan == "Yes").statement, db.engine)

    # Reorders the dataframe according to natural, human sorting by RSN
    df.rsn = df.rsn.astype('category')
    df.rsn.cat.reorder_categories(natural_sort(df.rsn), inplace=True, ordered=True)
    df.sort_values('rsn')

    df = df.rename(columns={'rsn': 'RSN', 'cap_points': 'Caps', 'recruit_points': 'Recruits', 'event_points': 'Events',
                            'xp_points': 'XP', 'rank': 'Rank', 'join_date': 'Join Date'})

    rank_pivot = pd.pivot_table(df, index=["RSN"],
                                     values=["Caps", "Recruits", "Events", "XP", "Rank", "Join Date"],
                                     aggfunc=max)

    rank_pivot = rank_pivot.reindex(columns=["Caps", "Recruits", "Events", "XP", "Rank", "Join Date"])
    rank_pivot.index.name = None

    return render_template('members/ranksheet.html',
                           rank_sheet=rank_pivot.to_html(classes='table table-hover table-condensed table-fixed', escape=False))