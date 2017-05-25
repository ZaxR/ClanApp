from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, DateField, IntegerField, SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app import models


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Login')


class CapsForm(FlaskForm):
    capdate = DateField('Cap Date', format='%m/%d/%Y')
    #week = StringField('Email Address', [validators.Length(min=0, max=35)])

    rsnchoices = [(account.rsn, account.rsn) for account in models.Accounts.query.all()]
    rsn = SelectField("RSN Choices", choices=rsnchoices, validators=[DataRequired()])

    captypechoices = [
        ('0', 'No'),
        ('1', 'New'),
        ('2', 'Vacation'),
        ('3', 'Yes')
    ]
    captype = SelectField("Cap Type Choices", choices=captypechoices, validators=[DataRequired()])

# validators.number_range(0, 3, message='Please select a valid cap type.'