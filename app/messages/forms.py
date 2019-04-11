from flask import request
from flask_wtf import FlaskForm
from wtforms import  TextAreaField, StringField, SubmitField
from wtforms.validators import DataRequired, Length
from ..models import User, Message

class MessageForm(FlaskForm):
    message = TextAreaField(('Message'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(('Submit'))
