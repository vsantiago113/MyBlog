from flask_wtf import FlaskForm
from flask import flash, g
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Regexp
from app.models import User
from flask_bcrypt import check_password_hash
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import IMAGES


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(min=6, max=250), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=32)])
    remember_me = BooleanField("Remember me", default=False)
    submit = SubmitField("Login")

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(
            email=self.email.data).first()
        if user is None:
            flash("Invalid username/password!", "danger")
            return False

        if not check_password_hash(user.password, self.password.data):
            flash("Invalid username/password!", "danger")
            return False

        self.user = user
        return True


class RegistrationForm(FlaskForm):
    username = StringField("Username",
                           validators=[DataRequired(), Length(min=3, max=24),
                                       Regexp("^[a-zA-Z0-9_.@]+$",
                                              message="Username must contain only letters numbers or underscore")
                                       ])
    email = StringField("Email Address", validators=[DataRequired(), Length(min=6, max=250), Email()])
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=8, max=32),
                                                         EqualTo("confirm", message="Passwords must match")])
    confirm = PasswordField("Repeat Password", validators=[DataRequired(), Length(min=8, max=32)])
    submit = SubmitField("Register")

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(
            username=self.username.data).first()
        if user:
            flash("Username is already in use!", "warning")
            return False

        user = User.query.filter_by(
            email=self.email.data).first()
        if user:
            flash("Email address has already been taken!", "warning")
            return False

        self.user = user
        return True


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired(), Length(min=3, max=32)])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('confirm_password',
                                                             message='Passwords must match!'), Length(min=3, max=32)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=3, max=32)])
    submit = SubmitField('Change Password')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if not check_password_hash(g.user.password, self.old_password.data):
            self.old_password.errors.append('Invalid password')
            return False

        self.user = None
        return True


class ChangeProfileImageForm(FlaskForm):
    image_name = FileField("Upload your photo", validators=[FileRequired(message="A photo is required!"),
                                                            FileAllowed(IMAGES, "File is not a valid image!")])
    submit = SubmitField('Upload')


class EditProfileForm(FlaskForm):
    first_name = StringField('First name', validators=[Length(min=3, max=32)])
    last_name = StringField('Last name', validators=[Length(min=3, max=32)])
    user_title = StringField('Title', validators=[Length(min=3, max=32)])
    submit = SubmitField('Update Profile')
