"""WTF-Forms for user input validation."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, TextAreaField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange


class LoginForm(FlaskForm):
    """Form for user login."""
    
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class SignupForm(FlaskForm):
    """Form for user signup."""
    
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=500)])
    usbc_id = StringField('USBC ID', validators=[Optional(), Length(max=50)])
    tnba_id = StringField('TNBA ID', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Sign Up')


class CreateUserForm(FlaskForm):
    """Form for creating new users."""
    
    email = EmailField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=500)])
    usbc_id = StringField('USBC ID', validators=[Optional(), Length(max=50)])
    tnba_id = StringField('TNBA ID', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Create User')


class SearchUserForm(FlaskForm):
    """Form for searching users."""
    
    search_type = SelectField('Search By', choices=[
        ('user_id', 'User ID'),
        ('email', 'Email'),
        ('usbc_id', 'USBC ID'),
        ('tnba_id', 'TNBA ID'),
        ('name', 'Name')
    ], validators=[DataRequired()])
    search_value = StringField('Search Value', validators=[DataRequired()])
    submit = SubmitField('Search')


class EditProfileForm(FlaskForm):
    """Form for editing user profiles."""
    
    first_name = StringField('First Name', validators=[Optional(), Length(max=100)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Profile')


class DeleteProfileForm(FlaskForm):
    """Form for deleting user profiles."""
    
    confirm = BooleanField('I understand this action cannot be undone', validators=[DataRequired()])
    submit = SubmitField('Delete Profile')


class MergeProfileForm(FlaskForm):
    """Form for merging user profiles."""
    
    main_user_id = IntegerField('Main User ID (keep this profile)', validators=[DataRequired(), NumberRange(min=1)])
    merge_user_ids = StringField('User IDs to Merge (comma-separated)', validators=[DataRequired()])
    submit = SubmitField('Merge Profiles')


class ListUsersForm(FlaskForm):
    """Form for listing users with filters."""
    
    first_name = StringField('First Name', validators=[Optional(), Length(max=100)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=100)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    address = StringField('Address', validators=[Optional(), Length(max=500)])
    usbc_id = StringField('USBC ID', validators=[Optional(), Length(max=50)])
    tnba_id = StringField('TNBA ID', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Filter Users')