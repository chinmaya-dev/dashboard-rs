from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, BooleanField, RadioField, IntegerField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from app.models import User, Comment
from flask_ckeditor import CKEditorField


class BlogForm(FlaskForm):
    city = StringField('City', validators=[DataRequired()])
    category = SelectField('Choose your blog subject', choices=[('Analytics', 'Analytics'), ('Web-Devlopment', 'Web Devlopment'),
                                                                ('Cloud', 'Cloud'), ('Automation', 'Automation'),  ('Mobile-Applications', 'Mobile Applications'), ('Data-Visualization', 'Data Visualization'), ('Process-Optimization', 'Process Optimization'), ('Security', 'Security'), ('Audit', 'Audit'), ('Pharma', 'Pharma'), ('Agriculture', 'Agriculture'), ('Blockchain', 'Blockchain'), ('IOT', 'Internt of things')])
    title = StringField('Blog Headline', validators=[DataRequired()])
    summary = TextAreaField('Short description ', validators=[DataRequired()])
    story = CKEditorField('Blog Text', validators=[DataRequired()])
    picture = FileField('Upload pictures', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Post')

class BlogCommentForm(FlaskForm):
    body = StringField('Enter your comment', validators=[DataRequired()])

    submit = SubmitField('Submit')
