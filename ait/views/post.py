from flask import Blueprint, render_template, abort, url_for, redirect, jsonify, request, flash
from flask_login import current_user, login_required
from firebase_admin import storage

from ait import db_fire
from ait.forms import PostForm

import os
import secrets
from io import BytesIO
from datetime import datetime

post =Blueprint('post',__name__)

@post.route('/get_post')
@login_required
def get_post():
    view_post = render_template('./post/view_post.html')
    data = {'remain': view_post}
    return jsonify(data)

def save_post_media(form_picture,username):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    blob = storage.bucket().blob('post/' +username + '/' + picture_fn)
    file_stream = BytesIO()
    form_picture.save(file_stream)
    blob.upload_from_string(
        file_stream.getvalue(),
        content_type=form_picture.content_type
    )
    blob.make_public()
    print(blob.public_url)

    return blob.public_url

@post.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if current_user.role != "Alumini":
        abort(403)
    form = PostForm()
    user_data = db_fire.collection(current_user.role).document(current_user.username).get().to_dict()
    if form.validate_on_submit():
            
        data = { "username" : current_user.username,
        "title" : form.title.data,
        "content" : form.content.data,
        "media" : '',
        "likes" : [],
        "comments" : {},
        "date_created" : datetime.utcnow(),
        "profile_url" : user_data['profile_url'],
        "post_id" : current_user.username + datetime.utcnow().strftime(r'%Y%m%d%H%M%S'),
        "role" : current_user.role,
        "url" : form.url.data,
        "post_type": form.post_type.data  # Saving the post type (Normal or Hiring)
        }
        # print(form.url.data)
        if form.picture.data:
            picture_file = save_post_media(form.picture.data, current_user.username)
            data['media'] = picture_file

        id = current_user.username + data['date_created'].strftime(r'%Y%m%d%H%M%S')
        db_fire.collection('post').document(id).set(data)
        flash('Post Added.', 'success')
        return redirect(url_for('home.home_latest'))
    return render_template('new_post.html', title='New Post',form=form, legend='New Post', user_data = user_data)




@post.route('/post/edit', methods=['GET', 'POST'])
@login_required
def edit_post():
    if current_user.role != "Alumini":
        abort(403)
    
    form = PostForm()
    user_data = db_fire.collection(current_user.role).document(current_user.username).get().to_dict()

    # Get the post_id from the request args
    post_id = request.args.get('post_id')
    # print("Editing Post-ID:", post_id)
 
    post_ref = db_fire.collection('post').document(post_id)
    post = post_ref.get().to_dict()

    if not post_id:
        flash('Invalid post ID!', 'danger')
        return redirect(url_for('home.home_latest'))

    # Restrict editing to the post creator
    if post['username'] != current_user.username:
        flash("You are not authorized to edit this post.", "danger")
        abort(403)

    if form.validate_on_submit():

        # print("Form title after submission:", form.title.data) 
        # print("Form content after submission:", form.content.data) 
        # Prepare the data for updating
        data = {
            "username": current_user.username,
            "title": form.title.data,
            "content": form.content.data,
            "media": '',
            "likes": post.get('likes', []),  # Keep existing likes
            "comments": post.get('comments', {}),  # Keep existing comments
            "date_created": datetime.utcnow(),
            "profile_url": user_data['profile_url'],
            "role": current_user.role,
            "url": form.url.data,
            "post_type": form.post_type.data
        }

        # print("Data being updated:", data)  # Debugging output

        # Update the existing post in Firestore
        try:
            post_ref.update(data)
            flash('Post updated successfully!', 'success')
        except Exception as e:
            print("Error during update:", e)
            flash('An error occurred while updating the post.', 'danger')

        return redirect(url_for('home.home_latest'))
    
    if post_id:
        # Fetch the existing post from Firestore
       
        # print("Post Data:", post)

        if not post:
            flash('Post not found!', 'danger')
            return redirect(url_for('home.home_latest'))

        # Populate the form with the existing post data
        form.title.data = post['title']
        form.url.data = post['url']
        form.content.data = post['content']
        form.post_type.data = post['post_type'] 

    return render_template('edit_post.html', title='Edit Post', form=form, legend='Edit Post', user_data=user_data, post_id=post_id)


@post.route('/delete/<string:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    # Fetch the post by post_id from the database
    post_ref = db_fire.collection('post').document(str(post_id))
    post = post_ref.get()

    if not post.exists:
        flash('Post not found!', 'danger')
        return redirect(url_for('home.home_latest'))

    post_data = post.to_dict()
    
    # Check if the current user is the post creator
    if post_data['username'] != current_user.username and current_user.email != 'admin_18185@apsit.edu.in':
        flash('You are not authorized to delete this post', 'danger')
        return redirect(url_for('home.home_latest'))

    try:
        # Admin can delete any post; creator can only delete their own post
        post_ref.delete()

        flash('Post deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred while deleting the post: {str(e)}', 'danger')

    return redirect(url_for('home.home_latest'))



@post.route('/comment/<string:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    if request.method == "POST":
        username = current_user.username
        date_created = datetime.utcnow()
        comment = request.form.get("comment")
        id = username + date_created.strftime(r'%Y%m%d%H%M%S')
        user_data = db_fire.collection(current_user.role).document(current_user.username).get().to_dict()

        data = {
            id :{
            "date_created" : date_created,
            "comment" : comment,
            "username" : current_user.username,
            "profile_url" : user_data['profile_url']
            }
        }
        db_fire.collection('post').document(post_id).set({"comments": data}, merge = True)
        flash('Comment Added.', 'success')
        return redirect(url_for('home.home_latest'))

@post.route('/like/<string:post_id>', methods=['POST'])
@login_required
def like(post_id):
        if request.method == "POST":
            result = db_fire.collection('post').document(post_id).get().to_dict()
            if current_user.username in result['likes']:
                temp = db_fire.collection('post').document(post_id).get().to_dict()['likes']
                temp.remove(current_user.username)
                db_fire.collection('post').document(post_id).set({'likes': temp}, merge =True)

            else:
                result['likes'].append(current_user.username)
                db_fire.collection('post').document(post_id).set(result, merge = True)
        flash('Post Liked.', 'success')
        return redirect(url_for('home.home_latest'))



