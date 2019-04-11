from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from app.models import User, Comment
from flask_ckeditor import CKEditorField


class PostForm(FlaskForm):
    city = StringField('City', validators=[DataRequired()])
    category = SelectField('Category', choices=[('Analytics', 'Analytics'), ('Web-Devlopment', 'Web Devlopment'),
                                                ('Cloud', 'Cloud'), ('Automation', 'Automation'),  ('Mobile-Applications', 'Mobile Applications'), ('Data-Visualization', 'Data Visualization'), ('Process-Optimization', 'Process Optimization'), ('Security', 'Security'),('Audit', 'Audit'), ('Pharma', 'Pharma'),('Agriculture','Agriculture')])
    title = StringField('Solution Headline', validators=[DataRequired()])
    summary = TextAreaField('Short description ', validators=[DataRequired()])
    story = CKEditorField('Solution Text', validators=[DataRequired()])
    picture = FileField('Upload pictures', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    body = StringField('Enter your comment', validators=[DataRequired()])
    submit = SubmitField('Submit')
