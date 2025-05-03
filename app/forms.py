# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    def validate_username(self, username):
        if User.find_by_username(username.data): raise ValidationError('Username taken.')
    def validate_email(self, email):
        if User.find_by_email(email.data): raise ValidationError('Email registered.')

class TicketForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    priority = SelectField('Priority', choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'), ('Critical', 'Critical')], validators=[DataRequired()])
    submit = SubmitField('Create Ticket')

class CommentForm(FlaskForm):
    text = TextAreaField('Add Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')

# UPDATED UpdateStatusForm
class UpdateStatusForm(FlaskForm):
     status = SelectField('Status', choices=[
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
        ('Reopened', 'Reopened') # <-- Added Reopened
        ], validators=[DataRequired()])
     submit = SubmitField('Update Status')