from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField
from wtforms.validators import DataRequired

from app import models


class NameChangeForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(NameChangeForm, self).__init__(*args, **kwargs)
        self.rsn.choices = [(account.rsn, account.rsn) for account in
                            models.Accounts.query.filter(models.Accounts.in_clan == 'Yes')]
        self.rsn.choices.sort(key=lambda t: tuple(t[0].lower()))

    change_date = DateField('Name Change Date', format='%Y/%m/%d')
    rsn = SelectField("RSN Choices", validators=[DataRequired()])
    new_name = StringField('New RSN', validators=[DataRequired()])


class DemographicsForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(NameChangeForm, self).__init__(*args, **kwargs)
        self.rsn.choices = [(account.rsn, account.rsn) for account in
                            models.Accounts.query.filter(models.Accounts.in_clan == 'Yes')]
        self.rsn.choices.sort(key=lambda t: tuple(t[0].lower()))

    # todo add all demographic fields to this form. On add/edit, looks up player associated with the account.
        # data is stored in Player and also pushed down to other accounts of the player