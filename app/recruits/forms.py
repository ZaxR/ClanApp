from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, DateField, IntegerField, SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app import models


class RecruitsForm(FlaskForm):
    recruit_date = DateField('Event Date', format='%m/%d/%Y')

    activity = SelectField("Activity Type Choices", choices=[('Join', 'Join'), ('Leave', 'Leave')],
                           validators=[DataRequired()])

    rsnchoices = [(account.rsn, account.rsn) for account in models.Accounts.query]
    rsnchoices.extend([('***Unknown***','***Unknown***'), ("***Alts***","***Alts***"), ("***Founder***","***Founder***")])
    rsnchoices.sort(key=lambda t: tuple(t[0].lower()))
    recruiter = SelectField("RSN Choices", choices=rsnchoices, validators=[DataRequired()])

    recruit = StringField('recruit', validators=[DataRequired()])