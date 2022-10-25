from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from diary.models import User, Project

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Regexp('^.{6,8}$', message='Your password should be between 6 and 8 characters long.')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Regexp('^.{6,8}$', message='Your password should be between 6 and 8 characters long.')])
    submit = SubmitField('Login')

def validate_email(self,email):
    user = User.query.filter_by(email=email.data).first()
    if user:
        raise ValidationError('This email is already registered to a user. Please use another email or login.')

class AddDiaryEntry(FlaskForm):
    related_project = SelectField('Related Project')
    tags = StringField('Tags',validators=[DataRequired(message='Enter any other related tags.')])
    entry_text = TextAreaField('Entry', validators=[DataRequired(message='Please enter your diary entry.')])
    submit = SubmitField('Submit Entry')

class AddProject(FlaskForm):
    project_title = StringField('Title', validators=[DataRequired(message='Please enter your project title.')])
    project_description = TextAreaField('Description', validators=[DataRequired(message='Please enter your project description.')])
    project_type = SelectField('Project Type', choices=['Novel', 'Short Fiction', 'Poetry', 'Essay', 'Other'] ,validators=[DataRequired(message='Please enter your project type.')])
    total_words_goal = StringField('Total Word Goal', validators=[DataRequired(message='Please enter your project word goal.')])
    total_words_current = StringField('Total Current Words', validators=[DataRequired(message='Please enter your current word count.')])
    weekly_words_goal = StringField('Weekly Word Goal', validators=[DataRequired(message='Please enter your weekly word goal.')])
    weekly_words_current = StringField('Weekly Current Words', validators=[DataRequired(message='Please enter your current weekly word count.')])
    google_drive = StringField('Google Drive Link', description='If this project is on Google Drive, enter its ID')
    submit = SubmitField('Submit Project')
