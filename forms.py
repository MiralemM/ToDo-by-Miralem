from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, BooleanField
from wtforms.validators import DataRequired


class SignInForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class TaskForm(FlaskForm):
    task_name = StringField("Add Task", validators=[DataRequired()])
    task_date = DateField("Select Date", format='%Y-%m-%d', validators=[DataRequired()])
    add_task = SubmitField("Add Task")
