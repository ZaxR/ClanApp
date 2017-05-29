import numpy as np
import pandas as pd
from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import desc

from app import db, models
from . import events
from app.events.forms import EventsForm


@events.route('/addevents', methods=['GET', 'POST'])
@login_required
def addevents():
    form = EventsForm(request.form)

    if request.method == 'POST' and form.validate():
        event_date = datetime.strftime(form.event_date.data, '%m/%d/%Y')
        new_recruit = models.Recruits(event_date,
                                      form.host.data,
                                      form.activity_type.data,
                                      form.description.data,
                                      form.attendee_count.data,
                                      points(form.attendee_count.data)
                                      )
        models.db.session.add(new_recruit)
        models.db.session.commit()
        flash('Event activity successfully added!')

        return redirect(url_for('events.addevents'))

    return render_template('events/addevents.html', form=form,
                           eventstable=models.Events.query.order_by(desc(models.Events.id)).limit(10).all())


def points(attendee_count):
    """Point awarded for joins, but taken away if the recruit leaves within 7 days"""
    if attendee_count >= 5:
        return 1
    return 0
