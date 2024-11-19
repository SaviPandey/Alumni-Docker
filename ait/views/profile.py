from flask import abort, redirect, render_template, Blueprint, request, url_for
from flask_login import current_user, login_required
from firebase_admin import storage

from ait import db_fire

import os
import secrets
from io import BytesIO

profile =Blueprint('profile',__name__)

def save_profile(form_picture,username):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    blob = storage.bucket().blob('profile_pic/'+ username + '/' + picture_fn)
    file_stream = BytesIO()
    form_picture.save(file_stream)
    blob.upload_from_string(
        file_stream.getvalue(),
        content_type=form_picture.content_type
    )
    blob.make_public()
    print(blob.public_url)
    return blob.public_url

@profile.route('/account')
@login_required
def account():
    user_data = db_fire.collection(current_user.role).document(current_user.username).get().to_dict()
    return render_template('users-profile.html', user_data = user_data)

@profile.route('/account/edit/<string:username>', methods=['POST'])
@login_required
def edit_account(username):
    if username != current_user.username:
        abort()
    if request.method == "POST":
        name = request.form.get("fullName")
        about = request.form.get("about")
        address = request.form.get("address")
        phone = request.form.get("phone")
        twitter = request.form.get("twitter")
        facebook = request.form.get("facebook")
        instagram = request.form.get("instagram")
        linkedin = request.form.get("linkedin")
        cv_link = request.form.get("cv_link")
        data ={
            'name' : name,
            'about' : about,
            'add' : address,
            'phone' : phone,
            'twitter' : twitter,
            'facebook' : facebook,
            'instagram' : instagram,
            'linkedin' : linkedin,
            'cv_link' : cv_link,
        }
        
        picture_url = request.files["picture_url"]
        if picture_url.filename:
            final = save_profile(picture_url, current_user.username)
            current_user.profile_url = final
            batch = db_fire.batch()
            docs = db_fire.collection('post').where('username', '==', current_user.username).get()

            for doc in docs:
                doc_ref = db_fire.collection('post').document(doc.id)
                doc_ref.update({'profile_url': final})
            batch.commit()

            data["profile_url"] = final
        
        db_fire.collection(current_user.role).document(username).set(data, merge = True)

    return redirect(url_for('profile.account'))


@profile.route('/user/<string:role>/<string:username>')
@login_required
def user(username,role):
    if username == current_user.username:
        return redirect (url_for('profile.account'))
    else:
        posts = db_fire.collection('post').where('username','==',username).get()
        user_data = db_fire.collection(current_user.role).document(current_user.username).get().to_dict()
        
        profile_data = db_fire.collection(role).document(username).get().to_dict()
        type = db_fire.collection('connection').document(current_user.username).get()
        
        value = False
        
        if type.exists:
            if username in type.to_dict().keys():
                value = True 
        return render_template('user.html', profile_data = profile_data,user_data = user_data, posts = posts, value = value  )

