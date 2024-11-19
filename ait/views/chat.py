from flask import render_template, Blueprint
from flask_login import current_user, login_required
from ait import db_fire, socketio
from flask_socketio import send

chat =Blueprint('chat',__name__)

@socketio.on("message")
def sendMessage(message):
    message = current_user.username+ ": " + message
    print(message)
    send(message, broadcast=True)

@chat.route('/chat')
@login_required
def chat_app():
    username = current_user.username
    user_data = db_fire.collection(current_user.role).document(current_user.username).get().to_dict()

    return render_template('chat.html', username = username, user_data = user_data)
    