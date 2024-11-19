from dotenv import load_dotenv
from flask import Blueprint, render_template, url_for, redirect, request, flash, session, abort
from flask_login import current_user, login_user, logout_user
# from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import requests
import pathlib
import time
from pip._vendor import cachecontrol
from google.oauth2 import id_token


from firebase_admin import auth
import pyrebase
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

from ait import db_fire
from ait.models import User
from ait import db_fire, pyrebase
from ait.forms import LoginForm, RegistrationForm, PasswordRestForm, EmailVerificationForm

import os
from datetime import date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()
authentication =Blueprint('authentication',__name__)
pyrebase_auth = pyrebase.auth()



#Google Authentication Part

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "451513964034-d4h0nenrrqqjfi2bsesg5ito1pme73n3.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],                           #"https://www.googleapis.com/auth/user.phonenumbers.read" and we need to enable google people api in google cloud console. and then we need to inculde the hashtagged in code
    redirect_uri="http://127.0.0.1:5000/callback"
)


def roleProvider(email):
    # year =int('20' + email.split('@')[0].split('_')[1][0:2])
    year = 2019
    currYear = int(date.today().year)

    if (year<currYear-4) :
        return 'Alumini'
    else :
        return 'Student'


def send_verification_email(email):
    sender = os.getenv('EMAIL')
    verification_link =auth.generate_email_verification_link(email)
    recipient = email
    subject = 'Verify your email for AIT-Website'

    body = f'''
    Hello {email.split('@')[0]},

    Follow this link to verify your email address.

    {verification_link}

    If you didn’t ask to verify this address, you can ignore this email.

    Thanks
    '''

    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = recipient
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = os.getenv('EMAIL')
    smtp_password = os.getenv('EMAIL_PWD')

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(sender, recipient, message.as_string())

def reset_password(email):
    sender = os.getenv('EMAIL')
    reset_link =auth.generate_password_reset_link(email)
    recipient = email
    subject = 'Reset your password for AIT-Website'

    body = f'''
    Hello {email.split('@')[0]},

    Follow this link to reset your email address.

    {reset_link}

    If you didn’t ask to reset this address, you can ignore this email.

    Thanks
    '''

    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = recipient
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = os.getenv('EMAIL')
    smtp_password = os.getenv('EMAIL_PWD')

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(sender, recipient, message.as_string())


@authentication.route('/login', methods= ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.home_latest'))
    form = LoginForm()
    if form.validate_on_submit():
        email =form.email.data
        password =form.password.data
        logging.info('User email: %s', email)
        # print(email)
        # print(password)
        try:
            user_id =auth.get_user_by_email(email)
        except:
            flash('User not found. Create Account.', 'info')
            return redirect(url_for('authentication.googleLogin'))
        
        print(user_id.email_verified)
        if (email == 'admin_18185@apsit.edu.in'):
            pass
        elif not(user_id.email_verified):
            flash('Verify your email.', 'info')
            return render_template('./auth_page/pages-login.html', title = 'Login', form=form)
            
        try:
            info= pyrebase_auth.sign_in_with_email_and_password(email, password)
            user_id =info['localId']
            print(user_id)
        
            user = User(user_id,email)
            # print(user)

            next_page = request.args.get('next')
            login_user(user, remember=form.remember.data)
            return redirect(next_page) if next_page else redirect(url_for('home.home_latest'))
        except Exception as e: 
            flash('Login Unsuccessful. Please check email and password', 'danger')
            print(e)
            return redirect(url_for('authentication.login'))
        
        
    return render_template('./auth_page/pages-login.html', title = 'Login', form=form)


@authentication.route("/googleLogin")
def googleLogin():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@authentication.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500) #state no match

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    # Verify the token with clock skew allowance
    try:
        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10  # Allow a 10-second skew
        )

        # Log issued at time and current time for debugging
        iat = id_info.get("iat")
        current_time = int(time.time())
        print(f"Token iat: {iat}, Current time: {current_time}")

    except Exception as e:
        print(f"Error verifying token: {e}")
        abort(500)  # Handle error appropriately

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")


    return redirect(url_for('authentication.register'))   
 

@authentication.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('authentication.login'))

@authentication.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home.home_latest'))
    
    email = session.get('email')

    form = RegistrationForm(email=email)

    if form.validate_on_submit():

        print(f"Password: {form.password.data}")
        print(f"Confirm Password: {form.confirm_password.data}")
        print(f"phone_number1: {form.phone_number1.data}")
        
        
        try:
            print(f"Email: {form.email.data}")
            email = form.email.data
            password = form.password.data
            full_name = form.full_name.data
            gender = form.gender.data
            branch = form.branch.data
            graduation_year = form.graduation_year.data
            phone_number1 = form.phone_number1.data
            country_code = form.country_code.data
            phone_number2 = form.phone_number2.data
            address = form.address.data
            city = form.city.data
            state = form.state.data

            # Optional fields for the second address
            outside_address = form.outside_address.data if form.outside_address.data else None
            optional_city = form.optional_city.data if form.optional_city.data else None
            optional_state = form.optional_state.data if form.optional_state.data else None

            # Work experience fields
            company_name = form.company_name.data
            role = form.role.data
            designation = form.designation.data
            joining_date = form.joining_date.data.isoformat()
            technology = form.technology.data

            # Role determination (assuming a roleProvider function exists)
            role = roleProvider(email)

            # Data to store in the database
            data = {
                "name": full_name,
                "username": email.split("@")[0],
                "email": email,
                "role": role,
                "gender": gender,
                "branch": branch,
                "graduation_year": graduation_year,
                "phone_number1": phone_number1,
                "country_code": country_code,
                "phone_number2": phone_number2,
                "address": address,
                
                "city": city,
                "state": state,
                "company_name": company_name,
                "role": role,
                "designation": designation,
                "joining_date": joining_date,
                "technology": technology,
                "profile_url": "",
                "verified": False
            }
            
            # Add optional address fields if provided
            if outside_address:
                data["optional_address"] = outside_address
            if optional_city:
                data["optional_city"] = optional_city
            if optional_state:
                data["optional_state"] = optional_state

            db_fire.collection(role).document(email.split("@")[0]).set(data)
            auth.create_user(email=email, password=password)
            send_verification_email(email)
            flash(f'Verification link sent to email.', 'info')
            return redirect(url_for('authentication.login'))
        
        except Exception as e:
            print(e)
            flash(f"An error occurred: {e}", 'danger')
    else:
        for field_name, errors in form.errors.items():
            print(f"{field_name}: {errors}")

    return render_template('./auth_page/pages-register.html', title='Register', form=form)


@authentication.route('/password_reset', methods= ['GET', 'POST'])
def password_reset():
    form = PasswordRestForm()
    if form.validate_on_submit():
        email =form.email.data
        try:
            auth.get_user_by_email(email)
        except:
            return redirect(url_for('authentication.register'))
        
        try:
            reset_password(email)
            return redirect(url_for('authentication.login'))
        except Exception as e: 
            flash('Login Unsuccessful. Please check email and password', 'danger')
            print(e)
            return redirect(url_for('authentication.login'))
        
    return render_template('./auth_page/pwd_reset.html', title = 'Password Reset', form=form)

@authentication.route('/send_verification_email', methods= ['GET', 'POST'])
def verify_email():
    form = EmailVerificationForm()
    if form.validate_on_submit():
        email =form.email.data
        try:
            auth.get_user_by_email(email)
        except:
            flash('User not found. Create Account.', 'info')
            return redirect(url_for('authentication.register'))
        
        try:
            print(email)
            send_verification_email(email)
            flash('Verification email send.', 'info')
            return redirect(url_for('authentication.login'))
        except Exception as e: 
            flash('Unable to send. Please check later.', 'danger')
            print(e)
            return redirect(url_for('authentication.login'))
        
    return render_template('./auth_page/verify_email.html', title = 'Verify Account', form=form)
