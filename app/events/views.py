from flask import redirect, render_template, request, url_for
from flask_login import login_required

from . import events
from app.events.forms import EventsForm


@events.route('/addevents', methods=['GET', 'POST'])
@login_required
def addevents():
    form = EventsForm(request.form)

    if request.method == 'POST' and form.validate():

        return redirect(url_for('events.addevents'))

    return render_template('events/addevents.html', form=form)

