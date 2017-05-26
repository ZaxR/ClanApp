from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, DateField, IntegerField, SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app import models


class EventsForm(FlaskForm):
    event_date = DateField('Event Date', format='%m/%d/%Y')

    rsnchoices = [(account.rsn, account.rsn) for account in models.Accounts.query.all()]
    host = SelectField("RSN Choices", choices=rsnchoices, validators=[DataRequired()])

    activity_type_choices = [
        ('Boss Mass', 'Boss Mass'),
        ('Drop Party', 'Drop Party'),
        ('House Party', 'House Party'),
        ('Mini Game', 'Mini game'),
        ('Recruiting', 'Recruiting'),
        ('Skilling Competition', 'Skilling Competition')
    ]
    activity = SelectField("Activity Type Choices", choices=activity_type_choices, validators=[DataRequired()])

    description = StringField('description', validators=[DataRequired()])

    attendee_count = IntegerField('attendee_count', validators=[DataRequired()])


# validators.number_range(0, 3, message='Please select a valid cap type.'