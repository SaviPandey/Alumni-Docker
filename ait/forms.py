from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import SelectMultipleField
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from firebase_admin import auth

from ait import db_fire
from ait.models import User

from datetime import datetime

class RegistrationForm(FlaskForm):
    full_name = StringField('Name',
                       validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )

    gender = SelectField(
        'Gender', 
        choices=[ 
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Others', 'Others')
        ],
        validators=[DataRequired(message="Please select a gender")]
    )

    branch = SelectField(
        'Branch',
        choices=[
            ('Computer', 'Computer'),
            ('IT', 'Information-Technology'),
            ('ECE', 'ECE'),
            ('CIVIL', 'Civil'),
            ('AIML', 'Computer(AIML)'),
            ('DS', 'Computer(DS)'),
            ('Mechanical', 'Mechanical')
        ],
        validators=[DataRequired(message="Please select a branch")]
    )

    graduation_year = SelectField(
        'Graduation Year', 
        choices=[
            ('2018', '2018'),
            ('2019', '2019'),
            ('2020', '2020'),
            ('2021', '2021'),
            ('2022', '2022'),
            ('2023', '2023'),
            ('2024', '2024'), 
            ('2025', '2025'), 
            ('2026', '2026')
        ], 
        validators=[DataRequired(message="Please select your graduation year")]
    )

    phone_number1 = StringField(
        'Mobile No.',
        validators=[DataRequired(message="Mobile number is required"), Length(min=10, max=10, message="Phone number must be exactly 10 digits")]
    )

    country_code = SelectField(
        'Country Code',
        choices=[ 
            ('+91', '+91 India'),
            ('+1', '+1 USA'),
            ('+44', '+44 UK'),
            ('+61', '+61 Australia'),
            ('+81', '+81 Japan'),
            ('+33', '+33 France'),
            ('+49', '+49 Germany'),
            ('+55', '+55 Brazil'),
            ('+27', '+27 South Africa'),
            ('+61', '+61 New Zealand')
        ],
        validators=[DataRequired()],
        default='+91'  # Set default country code to India
    )

    phone_number2 = StringField('Mobile No. (Secondary)', validators=[Length(max=10)])

    address = StringField('Address', validators=[DataRequired()])
                                      
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])

    outside_address = StringField('Outside Address',validators=[Length(max=100)])
    optional_city = StringField('Optional City')
    optional_state = StringField('Optional State')

    
    work_experience = StringField('Work Experience')
    company_name = StringField('Company Name')
    role = StringField('Role')
    designation = StringField('Designation')
    joining_date = DateField(
                    'Joining Date',
                    format='%Y-%m',
                    default=datetime.today,
                    validators=[DataRequired(message="Joining Date is required.")]
    )

    technology = SelectMultipleField(
        'Technology Currently Working On',
        choices=[
            ('MERN Stack', 'MERN Stack'),
            ('Python', 'Python'),
            ('Java', 'Java'),
            ('Flutter', 'Flutter'),
            ('MEAN Stack', 'MEAN Stack'),
            ('Django', 'Django'),
            ('Other', 'Other (Please specify)')
        ],
        validators=[DataRequired()]
    )
    other_tech_stack = StringField('Other Tech Stack')

    
    submit = SubmitField('Create Account')

    # def validate_email(self, email):
    #     try:
    #         user = auth.get_user_by_email(email.data)
    #     except Exception as e:
    #         user = False
        
    #     if user:
    #         raise ValidationError('That email is taken. Please choose a different one.')

    #     if '@' in email.data:
    #         apsit = email.data.split('@')[1]
    #     else:
    #         raise ValidationError('Enter valid email.')

    #     if apsit != 'apsit.edu.in':
    #         raise ValidationError('Only @apsit.edu.in email address allowed.')
    def validate_email(self, email):
        try:
            user = auth.get_user_by_email(email.data)
            print(user)
        except Exception as e:
            user = False
        
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

        # Check if email is valid
        if '@' not in email.data or '.' not in email.data.split('@')[-1]:
            raise ValidationError('Enter a valid email.')

        # Check if email is from gmail.com
        # if '@gmail.com' not in email.data:
        #     raise ValidationError('Only Gmail email addresses allowed.')

        
        
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    
    def validate_email(self, email):
        if '@' in email.data:
            apsit = email.data.split('@')[1]
        else: 
            raise ValidationError('Enter valid email.')
        
        # if '_' not in email.data.split('@')[0] or len(email.data.split('@')[0].split('_')[1])!=5:
        #     raise ValidationError('Enter valid email.')

        # if apsit != 'apsit.edu.in':
        #     raise ValidationError('Only @apsit.edu.in email address allowed.')
        
    submit = SubmitField('Login')

class PasswordRestForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    def validate_email(self, email):
        if '@' in email.data:
            apsit = email.data.split('@')[1]
        else: 
            raise ValidationError('Enter valid email.')
        
        # if '_' not in email.data.split('@')[0] or len(email.data.split('@')[0].split('_')[1])!=5:
        #     raise ValidationError('Enter valid email.')

        # if apsit != 'apsit.edu.in':
        #     raise ValidationError('Only @apsit.edu.in email address allowed.')
    
    submit = SubmitField('Reset')
    
class EmailVerificationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    def validate_email(self, email):
        if '@' in email.data:
            apsit = email.data.split('@')[1]
        else: 
            raise ValidationError('Enter valid email.')
        

        # if apsit != 'apsit.edu.in':
        #     raise ValidationError('Only @apsit.edu.in email address allowed.')
        
        # if '_' not in email.data.split('@')[0] or len(email.data.split('@')[0].split('_')[1])!=5:
        #     raise ValidationError('Enter valid email.')
        
    submit = SubmitField('Send')
    
class UpdateAccountForm(FlaskForm):
    name = StringField('Username')
    about = StringField('About')
    address = StringField('Address')
    phone = StringField('Phone')
    twitter = StringField('Twitter')
    facebook = StringField('Facebook')
    instagram = StringField('Instagram')
    linkedin = StringField('LinkedIn')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_phone(self, phone):
        if len(phone.data) != 10:
            raise ValidationError('Enter valid phone number.')
            
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    url = StringField('URL')
    content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('Upload Media', validators=[FileAllowed(['jpg', 'png','mp4','jpeg','svg','webp'], 'Only media files are allowed.')])

    # New field for post type
    post_type = SelectField(
        'Post Type',
        choices=[('normal', 'Normal Post'), ('hiring', 'Hiring Post')],
        validators=[DataRequired()]
    )

    submit = SubmitField('Post')