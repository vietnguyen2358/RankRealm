import datetime, bcrypt
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Define a user schema
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(150))
    player_performances = db.relationship('PlayerPerformance', backref='user', lazy='dynamic')
    hosted_events = db.relationship('Event', backref='host', lazy='dynamic')
    player_performances = db.relationship('Event', backref='player', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)

# Define a game schema
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    description = db.Column(db.String(10000))
    release_date = db.Column(db.DateTime())
    leaderboards = db.relationship('Leaderboard', backref='game', lazy='dynamic')
    events = db.relationship('Event', backref='game', lazy='dynamic')

# Define a leaderboard schema
class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    player_performances = db.relationship('PlayerPerformance', backref='leaderboard', lazy='dynamic')

# Define a player performance schema
class PlayerPerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    elo_rating = db.Column(db.Integer)
    matches_played = db.Column(db.Integer)
    matches_won = db.Column(db.Integer)
    matches_lost = db.Column(db.Integer)

# Define a event schema
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_date = db.Column(db.DateTime())
    end_date = db.Column(db.DateTime())