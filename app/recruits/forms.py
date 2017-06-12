from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField
from wtforms.validators import DataRequired

from app import models


class RecruitsForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(RecruitsForm, self).__init__(*args, **kwargs)
        self.recruiter.choices = [(account.rsn, account.rsn) for account in
                                  models.Accounts.query]  # .filter(models.Accounts.in_clan == 'Yes')]
        self.recruiter.choices.extend([('***Unknown***', '***Unknown***'),
                                       ("***Alts***", "***Alts***"), ("***Founder***", "***Founder***")])
        self.recruiter.choices.sort(key=lambda t: tuple(t[0].lower()))

    recruit_date = DateField('Event Date', format='%Y/%m/%d')

    activity = SelectField("Activity Type Choices", choices=[('Join', 'Join'), ('Leave', 'Leave')],
                           validators=[DataRequired()])

    recruiter = SelectField("RSN Choices", validators=[DataRequired()])

    recruit = StringField('recruit', validators=[DataRequired()])
