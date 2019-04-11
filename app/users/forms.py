from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, IntegerField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user




class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    about_me = StringField('About you', validators=[DataRequired()])
    web_url = StringField('website URL')
    gender = RadioField('Gender', choices = [('Male','Male'),('Female','Female')], validators=[DataRequired()])
    contact_number = IntegerField("phone number", validators=[DataRequired()])
    date_of_birth = DateField('date of birth', format="%Y-%m-%d")
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != User.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_username(self, email):
        if email.data != User.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')





class LinksForm(FlaskForm):
    facebook_id = StringField('link Facebook')
    twitter_id = StringField('Link Twitter')
    instagram_id = StringField(' Link Instagram ')
    snapchat_id = StringField(' Link Snapchat ')
    submit = SubmitField('Update')

class IntrestForm(FlaskForm):
    intrest_type = StringField('Intrest name')
    submit = SubmitField('Update')



class EventsForm(FlaskForm):
    event_name = StringField('Event Name')
    event_description = StringField('Event description')
    event_location = StringField('location')
    event_start_date = DateField(' Start Date', format="%Y-%m-%d")
    event_end_date = DateField(' End Date', format="%Y-%m-%d")
    event_status = BooleanField('Event Status')
    submit = SubmitField('Update')



class MediaForm(FlaskForm):
    image = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png'])])
    media_format = SelectField('Media type ', choices = [('image', 'image')])
    submit = SubmitField('upload')


