from flask import request
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField
from wtforms.validators import DataRequired, Email

class InputTextForm(FlaskForm):
  inputText = TextAreaField(validators=[DataRequired()])

class SearchForm(FlaskForm):
    q = StringField(('Search Stories & People'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class MessageForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    name = StringField('Name',
                        validators=[DataRequired()])
    msg = TextAreaField('Message',
                      validators=[DataRequired()])
    submit = SubmitField('Send message')
