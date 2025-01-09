from flask import Blueprint, jsonify
from flask_login import current_user, login_required
from ait import db_fire
from datetime import datetime

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notifications',methods = ['GET'])
def fetch_notifications():
    """
    Fetches notifications for the logged-in user.
    """
    notification_ref = db_fire.collection('notifications').document(current_user.username)
    notification_doc = notification_ref.get()

    if notification_doc.exists:
        notifications = notification_doc.to_dict().get('notifications', [])
    else:
        notifications = []

    return jsonify({'notifications': notifications})


@notification_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_as_read():
    """
    Marks all notifications as read for the logged-in user.
    Sets their read status to True without auto-deleting old notifications.
    """
    try:
        notification_ref = db_fire.collection('notifications').document(current_user.username)
        notification_doc = notification_ref.get()

        if not notification_doc.exists:
            return jsonify({'message': 'No notifications found for the user.'}), 404

        notifications = notification_doc.to_dict().get('notifications', [])

        
        for notification in notifications:
            notification['read'] = True

       
        notification_ref.set({'notifications': notifications}, merge=True)

        return jsonify({
            'message': f'{len(notifications)} notifications are marked as read.',
            'read_count': len(notifications)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def create_notification(username, message):
    """
    Creates a notification for the specified user.
    """
    notification_ref = db_fire.collection('notifications').document(username)
    notification_doc = notification_ref.get()

    new_notification = {
        'message': message,
        'timestamp': datetime.utcnow(),
        'read': False
    }

    if notification_doc.exists:
        notifications = notification_doc.to_dict().get('notifications', [])
        notifications.append(new_notification)
        notification_ref.set({'notifications': notifications}, merge=True)
    else:
        notification_ref.set({'notifications': [new_notification]}, merge=True)
