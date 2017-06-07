from io import StringIO
from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
import pandas as pd
from requests import get
from sqlalchemy import desc, exists
from sqlalchemy.orm import mapper

from app import db, models
from . import xp


@xp.route('/xp', methods=['GET', 'POST'])
@login_required
def xp():
    try:
        r = get("http://services.runescape.com/m=clan-hiscores/members_lite.ws?clanId=374374&ranking=1&pageSize=500")
        pull = pd.read_csv(StringIO(r.text), sep=",")
        pull.columns = ['rsn', 'Rank', 'xp', 'Kills']
        xp = pull[['rsn', 'xp']]
        xp['xp'] = xp['xp'].apply(lambda x: num_format(x))  # xp['XP'] = xp.loc[1:,['XP']].apply(lambda x: num_format(x))
        xp['time_stamp'] = [datetime.now() for _ in xp['xp']]  # xp.loc[:,['XP']]]
        xp.to_sql(name='xp', con=db.engine, if_exists='replace', index=False)
        # todo use db.session.merge(xp) or other upsert instead of replace to keep former clannie xp
        # would allow to see name changes based on xp of old and new being ==
        # would allow keeping historic xp for players no longer in clan without writing to Account xp_pts
    except:
        print('Was an issue. Pulling old numbers from query instead')
        xp = pd.read_sql(models.XP.query.order_by(models.XP.rsn).statement, db.engine)


    return render_template('xp/xp.html', action="xp.xp",
                           xp_table=xp.to_html(classes='table table-hover table-condensed'))

def num_format(num):
    magnitude = 0
    while num >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'k', 'm', 'b'][magnitude])


# todo columns to add to xp: xp/day in clan, formatted xp column, timestamp