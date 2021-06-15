from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, HiddenField
from wtforms.validators import DataRequired, Length, Email

class GroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Save')

class UserForm(FlaskForm):
    id = HiddenField()
    username = StringField('Username', validators=[DataRequired(), Length(max=20, min=6)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    groupids = StringField('Group')
    submit = SubmitField('Save')

