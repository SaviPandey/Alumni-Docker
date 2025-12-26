from flask import Flask, send_from_directory
from flask_login import LoginManager
from flask_socketio import SocketIO, send
import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore
import pyrebase

# from dotenv import load_dotenv

from cryptography.fernet import Fernet
import os
import json
from datetime import datetime

# load_dotenv()

with open(
        os.path.join(os.path.dirname(__file__),
                     'config/firebase_config.json')) as f:
    firebase_config = json.loads(f.read())

with open(
        os.path.join(os.path.dirname(__file__),
                     'config/admin_config.json')) as f:
    admin_config = json.loads(f.read())



# firebase_config = os.getenv("FIREBASE_CONFIG")
# admin_config =  os.getenv("ADMIN_CONFIG")


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

app.config['SECRET_KEY'] = "abcde"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

cred = credentials.Certificate(admin_config)

firebase_admin.initialize_app(
    cred, {'storageBucket': 'alumni-portal-70263.appspot.com'})
pyrebase = pyrebase.initialize_app(firebase_config)

db_fire = firestore.client()
login_manager = LoginManager(app)
login_manager.login_view = 'authentication.login'
login_manager.login_message_category = 'info'

from ait.views import authentication, chat, connection, error_handling, home, post, profile

app.register_blueprint(authentication.authentication)
app.register_blueprint(chat.chat)
app.register_blueprint(connection.connect)
app.register_blueprint(error_handling.error_handling)
app.register_blueprint(home.home)
app.register_blueprint(post.post)
app.register_blueprint(profile.profile)

# Health check endpoint for monitoring
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Alumni Portal'
    }
