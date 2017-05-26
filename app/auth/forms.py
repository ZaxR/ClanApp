from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, DateField, IntegerField, SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app import models


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Login')