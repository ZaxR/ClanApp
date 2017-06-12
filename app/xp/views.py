from datetime import datetime
from io import StringIO, BytesIO

import pandas as pd
import re
from flask import render_template
from flask_login import login_required
from requests import get

from app import db, models
from . import xp
from app.caps.views import natural_sort


@xp.route('/xp', methods=['GET', 'POST'])
@login_required
def xp():
    try:
        r = get("http://services.runescape.com/m=clan-hiscores/members_lite.ws?clanId=374374&ranking=1&pageSize=500")
        pull = pd.read_csv(StringIO(r.text), sep=",")   # r.text.encode('utf-8')

        pull.columns = ['rsn', 'Rank', 'xp', 'Kills']
        xp_df = pull[['rsn', 'xp', 'Rank']]
        #xp['xp'] = xp['xp'].apply(lambda x: num_format(int(x)))  # xp['XP'] = xp.loc[1:,['XP']].apply(lambda x: num_format(x))
        xp_df['time_stamp'] = [datetime.now() for _ in xp_df['xp']]  # xp.loc[:,['XP']]]
        xp_df.to_sql(name='xp', con=db.engine, if_exists='replace')  # , index=False

    except:
        print('Was an issue. Pulling old numbers from query instead')
        xp_df = pd.read_sql(models.XP.query.order_by(models.XP.rsn).statement, db.engine)

    # # Adds the activity to the Recruits table
    for record in [rsn for rsn in models.XP.query.all()]:
        match = models.Accounts.query.filter(models.Accounts.rsn.ilike(record.rsn.replace(" ", "_") + "%")).first()
        if match is not None:
            match.xp_points = record.xp
            match.rank = record.rank
            models.db.session.commit()


    return render_template('xp/xp.html', action="xp.xp",
                           xp_table=xp_df.to_html(classes='table table-hover table-condensed'))

def num_format(num):
    magnitude = 0
    while num >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'k', 'm', 'b'][magnitude])


# todo columns to add to xp: xp/day in clan, formatted xp column, timestamp