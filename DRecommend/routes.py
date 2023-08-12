import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, send_file
from DRecommend import app, db, bcrypt
from DRecommend.forms import RegistrationForm, LoginForm, SearchForm, UpdateAccountForm
from DRecommend.models import User,Follower,Song
from flask_login import login_user, current_user, logout_user, login_required
           

def genreFilter(sample_list,songs):
    filteredList=[]
    for song in songs:
        for follower_pick in sample_list:
            if (follower_pick.genre==song.genre) and (follower_pick not in filteredList):
                filteredList.append(follower_pick)

    return filteredList           

def recommondations(followers,songs):
    sample_list=[]
    for follower in followers:
        follower_user=User.query.get(follower.follower_user_id)
        follower_picks=follower_user.listening
        for follower_pick in follower_picks:
            if (follower_pick not in sample_list):
                sample_list.append(follower_pick) 

    sample_list2 = genreFilter(sample_list,songs)
    

    return sample_list2

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    user=User.query.filter_by(username=current_user.username).first()
    followers=user.followers
    songs=user.listening
    recommended=recommondations(followers,songs)
    return render_template('home.html',followers=followers,user=user,songs=songs,recommended=recommended)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccesful, Please check username and password','danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    user=User.query.filter_by(username=current_user.username).first()
    followers=user.followers
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            follower_instances=Follower.query.filter_by(username=current_user.username).all()
            for instance in follower_instances:
                instance.image_file = picture_file
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form,followers=followers)

@app.route("/account/<int:user_id>", methods=['GET', 'POST'])
@login_required
def user_account(user_id):
    current=User.query.filter_by(username=current_user.username).first()
    followers=current.followers
    user=User.query.get(user_id)
    songs=user.listening
    image_file=url_for('static',filename='profile_pics/'+ user.image_file)
    return render_template('user_account.html', title=user.username, user=user, image_file=image_file,songs=songs,followers=followers)

@app.route("/search", methods=['GET', 'POST'])
def search():
    current=User.query.filter_by(username=current_user.username).first()
    followers=current.followers
    form=SearchForm()
    user={}
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.user.data).first()
    return render_template('search.html',form=form, user=user, followers=followers)

@app.route("/follow_user/<int:user_id>", methods=['GET', 'POST'])
@login_required
def follow_user(user_id):
    current=User.query.filter_by(username=current_user.username).first()
    user=User.query.get(user_id)
    if user == current_user:
        abort(403)
    follower=Follower(username=current.username, email=current.email,image_file=current.image_file,follower_user_id=current.id,following=user)
    db.session.add(follower)
    db.session.commit()
    flash(f'You are now following {user.username}','info')
    return redirect(url_for('home'))

@app.route("/pick_songs", methods=['GET', 'POST'])
@login_required
def pick_songs():
    current=User.query.filter_by(username=current_user.username).first()
    followers=current.followers
    songs=Song.query.all()
    return render_template('pick_song.html',songs=songs,user=current,followers=followers)

@app.route("/add_song/<int:user_id>/<int:song_id>", methods=['GET', 'POST'])
@login_required
def add_song(user_id,song_id):
    user=User.query.get(user_id)
    song=Song.query.get(song_id)
    user.listening.append(song)
    db.session.commit()
    flash(f'{song.song_name} has been added to Your Picks')
    return redirect(url_for('home'))