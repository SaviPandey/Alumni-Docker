from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from ait import db_fire
from firebase_admin import firestore

home =Blueprint('home',__name__)

@home.route('/')
# @home.route('/home/latest')
# @login_required
# def home_latest():
#     filter1 = request.args.get('branch')
#     filter2 = request.args.get('graduation_year')

#     user_data = db_fire.collection(current_user.role).document(current_user.username).get().to_dict()
#     posts = db_fire.collection('post').order_by("date_created", direction=firestore.Query.DESCENDING).get()

#     filtered_posts = []

#     for post in posts:
#         post_data = post.to_dict()
#         post = post_data
#         user_data = db_fire.collection('Alumini').document(post['username']).get().to_dict()
#         # Check filter conditions
#         if filter1 and user_data['branch'] != filter1:
#             continue 
#         if filter2 and user_data['graduation_year'] != filter2:
#             continue 

#         # If post matches the filters, add it to the filtered_posts list
#         filtered_posts.append(post_data)

#     return render_template('home.html', title='Home', user_data=user_data, posts=filtered_posts)

@home.route('/home/latest')
@login_required
def home_latest():
    filter1 = request.args.get('branch')
    filter2 = request.args.get('graduation_year')

    # Get current user's data
    user_data = db_fire.collection(current_user.role).document(current_user.username).get().to_dict()

    posts = db_fire.collection('post').order_by("date_created", direction=firestore.Query.DESCENDING).get()

    filtered_posts = []

    for post in posts:
        post_data = post.to_dict()
        
        # Get the user data of the person who posted the post
        post_user_data = db_fire.collection('Alumini').document(post_data['username']).get().to_dict()
        
        # Check filter conditions
        if filter1 and post_user_data['branch'] != filter1:
            continue 
        if filter2 and post_user_data['graduation_year'] != filter2:
            continue 

        filtered_posts.append(post_data)

    return render_template('home.html', title='Home', user_data=user_data, posts=filtered_posts)



@home.route('/home/top')
@login_required
def home_top():
    user_data = db_fire.collection(current_user.role).document(current_user.username).get().to_dict()
    posts = db_fire.collection("post").order_by("likes", direction=firestore.Query.DESCENDING).get()

    return render_template('home_top.html', title = 'Home', user_data = user_data, posts = posts)

@home.route('/home/myPost')
@login_required
def home_myPost():

    user_data = db_fire.collection(current_user.role).document(current_user.username).get().to_dict()

    posts = db_fire.collection('post').where('username', '==', current_user.username).order_by('date_created', direction=firestore.Query.DESCENDING).get()

    filtered_posts = []

    for post in posts:
        post_data = post.to_dict()

        print(post_data)
        
        if post_data['username'] == current_user.username:
            filtered_posts.append(post_data)

    return render_template('home_myPost.html', title='My Posts', user_data=user_data, posts=filtered_posts)



