from DRecommend import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

user_song=db.Table('user_song',
                   db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                   db.Column('song_id', db.Integer, db.ForeignKey('song.id'))
                   )

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    followers = db.relationship('Follower', backref='following', lazy=True)
    listening = db.relationship('Song', secondary=user_song, backref='listeners')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    follower_user_id= db.Column(db.Integer, nullable=False)
    following_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(20), unique=True, nullable=False)
    artist = db.Column(db.String(20), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    genre = db.Column(db.String(20), nullable=False)
