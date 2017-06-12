import pandas as pd
from datetime import datetime
from app import models
from app.caps.views import possible_caps, cap_count, cap_percentage, cap_streak, last_cap

"""
To load recruits and accounts tables, save a file called "recruitsdata.csv" in the main ClanApp folder,
with columns as follows:
recruit_date	activity_type	recruiter	recruit	points	change_to_recruit_count

Dates should be formatted YYYY-MM-DD in Excel formatting.
"""
# df = pd.read_csv('C:/Users/Zax/Desktop/recruitsdata.csv')
#
# # Adds the activity to the Recruits table
# for index, row in df.iterrows():
#     recruit_date = datetime.strptime(row['recruit_date'], '%Y-%m-%d').date()
#     activity_type = row['activity_type']
#     recruiter = row['recruiter']
#     recruit = row['recruit']
#     points = row['points']
#     change_to_recruit_count = row['change_to_recruit_count']
#
#     new_recruit = models.Recruits(recruit_date, activity_type, recruiter, recruit, points, change_to_recruit_count)
#     models.db.session.add(new_recruit)
#
# models.db.session.commit()

# df.index.names=['id']
# df.to_sql(name='recruits', con=db.engine, if_exists='replace', index=True, dtype={'id': types.INTEGER()})

recruits = models.Recruits.query.order_by(models.Recruits.recruit_date)
for recruit in recruits:
    if recruit.activity_type == 'Join':
        new_account = models.Accounts(rsn=recruit.recruit, in_clan='Yes', join_date=recruit.recruit_date)
        models.db.session.add(new_account)
        print('Writing join for ', recruit.recruit)
        models.db.session.commit()
    else:
        print('Writing leave for ', recruit.recruit)
        name = recruit.recruit.replace(" ", "_")
        account = models.Accounts.query.filter(models.Accounts.rsn.ilike(name+"%")).first()
        account.in_clan = 'No'
        account.leave_date = recruit.recruit_date
        models.db.session.commit()

# """
# Imports all caps in order, including analytics
# """
#
# def date_for_week(wk, clanstart='2016-5-3'):
#     from datetime import datetime, timedelta
#     wk_days = int(wk.replace('Wk ','')) * 7 - 7
#     d0 = datetime.strptime(clanstart, '%Y-%m-%d').date()
#     return d0 + timedelta(days=wk_days)
#
# df_caps = pd.read_csv('C:/Users/Zax/Desktop/capsdata_stacked.csv')
#
# # Properly sorts by week, so when added to the db, analytics (such as streak) are calculated properly (in order)
# df_caps['sorted_weeks'] = df_caps['week'].apply(lambda x: int(x.replace('Wk ','')))
# df_caps = df_caps.sort_values(by='sorted_weeks').drop('sorted_weeks', axis=1)
#
# # # Reorders the dataframe according to natural, human sorting by RSN
# # df_caps.week = df_caps.week.astype('category')
# # df_caps.week.cat.reorder_categories(natural_sort(df_caps.week), inplace=True, ordered=True)
# # df_caps.sort('week')
#
# for index, row in df_caps.iterrows():
#     rsn = row['rsn']
#     date = date_for_week(row['week'])
#     week = row['week']
#     cap_type = row['captype']
#     caps_possible = possible_caps(rsn, date, "Add")
#     count_caps = cap_count(rsn, date, cap_type, "Add")
#     percentage_capped = cap_percentage(count_caps, caps_possible)
#     streak = cap_streak(rsn, date, cap_type, "Add")
#     recent_cap = last_cap(rsn, date, cap_type, "Add")
#
#     add_cap = models.Caps(date, week, rsn, cap_type, caps_possible, count_caps, percentage_capped, streak, recent_cap)
#     models.db.session.add(add_cap)
#     models.db.session.commit()