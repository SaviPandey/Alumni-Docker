from flask import Blueprint, render_template
from flask_login import current_user
from ait import db_fire

error_handling =Blueprint('error_handling',__name__)

@error_handling.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    user_data = db_fire.collection(current_user.role).document(current_user.username).get().to_dict()
    return render_template('pages-error-404.html', user_data = user_data), 404