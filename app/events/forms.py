from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, DateField, IntegerField, SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app import models


class EventsForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(EventsForm, self).__init__(*args, **kwargs)
        self.host.choices = [(account.rsn, account.rsn) for account in models.Accounts.query.all()]
        self.host.choices.sort(key=lambda t: tuple(t[0].lower()))

    event_date = DateField('Event Date', format='%Y/%m/%d')

    host = SelectField("RSN Choices", validators=[DataRequired()])

    activity_type_choices = [('Boss Mass', 'Boss Mass'), ('Drop Party', 'Drop Party'), ('House Party', 'House Party'),
                             ('Mini Game', 'Mini game'), ('Recruiting', 'Recruiting'),
                             ('Skilling Competition', 'Skilling Competition')]
    activity_type = SelectField("Activity Type Choices", choices=activity_type_choices, validators=[DataRequired()])

    description = StringField('description', validators=[DataRequired()])

    attendee_count = IntegerField('attendee_count', validators=[DataRequired()])
