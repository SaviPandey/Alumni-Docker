from flask import Blueprint, render_template, abort, url_for, redirect, request, flash
from flask_login import current_user, login_required
from ait import db_fire
from datetime import datetime
from ait.models import User

from datetime import date

connect =Blueprint('connection',__name__)

def roleProvider(username):
    # Trial Year static
    year = 2019
    try:
        # passYear =username.split('_')[1][0:2]
        # year =int('20' + passYear)
        currYear = int(date.today().year)

        if (year<currYear-4) :
            return 'Alumini'
        else :
            return 'Student'
    except:
        return None
    


@connect.route('/connection')
@login_required
def connection():
    doc_ref = db_fire.collection('connection').document(current_user.username)
    doc = doc_ref.get()
    type = db_fire.collection('connection').document(current_user.username).get().to_dict()
    print(type)
    user_data = db_fire.collection(current_user.role).document(current_user.username).get().to_dict()
    return render_template('connection.html', user_data = user_data, type = type)

@connect.route('/connection/send/<string:username>')
@login_required
def send_req(username):
    if username == current_user.username:
        abort(403)
    else:
        doc_ref =   db_fire.collection('connection').document(current_user.username)
        user_data = db_fire.collection('Alumini').document(username).get().to_dict()
        data = db_fire.collection('connection').document(current_user.username).get()
        
        if data.exists:
            print(data.to_dict())
            temp = data.to_dict()
            if user_data['username'] in data.to_dict().keys():
                print("hello in userdata")
                temp.pop(user_data['username'])
            
            else:    
                temp.update({ 
                    user_data['username'] :{
                    'username' : user_data['username'],
                    'profile_url' : user_data['profile_url'],
                    'created_at' : datetime.utcnow()
                    }
                    })
            db_fire.collection('connection').document(current_user.username).set( temp ,merge = True)
            
        else:
            temp = { 
                user_data['username'] :{
                'username' : user_data['username'],
                'profile_url' : user_data['profile_url'],
                'created_at' : datetime.utcnow()
                }
                }
            doc_ref.set(temp, merge = True)
                
        role = 'Alumini'
        return redirect(url_for('profile.user',username = username, role = role))

@connect.route('/connection/remove/<string:username>')
@login_required
def remove_req(username):
    if username == current_user.username:
        abort(403)
    else:
        data_user = db_fire.collection('connection').document(current_user.username).get().to_dict()
        print(data_user)
        print(type(data_user))
        del data_user[username]
        print(data_user)
        db_fire.collection('connection').document(current_user.username).set( data_user)
        role = 'Alumini'
        return redirect(url_for('profile.user',username = username, role = role))

@connect.route('/connection/<string:type>/<string:username>')
@login_required
def action_req(username,type):
    if username == current_user.username:
        abort(403)
    else:
        doc_ref =   db_fire.collection('connection').document(current_user.username)
        doc = doc_ref.get()

        if doc.exists:
            if type == "accept":
                data = doc.to_dict()['pending']
                data.remove(username)
                
                if 'accept' in doc.to_dict().keys():
                    accept_data = doc.to_dict()['accept']
                    accept_data.connectionend(username)
                else:
                    accept_data = [username]
                
                doc_ref.set({'accept': accept_data},merge = True)
                doc_ref.set({'pending': data},merge = True)

            if type == "reject":
                data = doc.to_dict()['pending']
                data.remove(username)
                doc_ref.set({'pending': data},merge = True)

        return redirect(url_for('home.home_latest'))
    
@connect.route('/search/<string:username>', methods=['GET','POST'])
@login_required
def search_user(username):
        role =roleProvider(username)
        if (role==None):
            flash('Invalid Username.','danger')
            return redirect(url_for('home.home_latest'))
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
            # print(profile_data)
            return render_template('user.html', profile_data = profile_data,user_data = user_data, posts = posts, value = value  )