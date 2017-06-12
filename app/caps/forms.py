from flask_wtf import FlaskForm
from wtforms import DateField, SelectField
from wtforms.validators import DataRequired

from app import models


class CapsForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(CapsForm, self).__init__(*args, **kwargs)
        self.rsn.choices = [(account.rsn, account.rsn) for account in models.Accounts.query.all()]
        self.rsn.choices.sort(key=lambda t: tuple(t[0].lower()))

    capdate = DateField('Cap Date', format='%Y/%m/%d')
    # week = StringField('Cap Week', validators=[DataRequired()])

    rsn = SelectField("RSN Choices", validators=[DataRequired()])

    captypechoices = [
        ('No', 'No'),
        ('New', 'New'),
        ('Vacation', 'Vacation'),
        ('Yes', 'Yes')
    ]
    captype = SelectField("Cap Type Choices", choices=captypechoices, validators=[DataRequired()])
