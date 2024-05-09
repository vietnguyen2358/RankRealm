from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from . import db
from .models import Game, Leaderboard, PlayerScore

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html", user=current_user)

@views.route('/games')
def games():
    games = Game.query.all()
    leaderboards = {}
    for game in games:
        leaderboard = Leaderboard.query.filter_by(game_id=game.id).first()
        if leaderboard:
            player_scores = PlayerScore.query.filter_by(leaderboard_id=leaderboard.id).order_by(PlayerScore.elo_rating.desc()).limit(10).all()
            leaderboards[game.id] = player_scores
    return render_template('games.html', games=games, leaderboards=leaderboards, current_user=current_user)

@views.route('/join-game/<int:game_id>', methods=['POST'])
def join_game(game_id):
    if current_user.is_authenticated:
        game = Game.query.get(game_id)
        if game:
            leaderboard = Leaderboard.query.filter_by(game_id=game.id).first()
            if leaderboard:
                existing_player_score = PlayerScore.query.filter_by(leaderboard_id=leaderboard.id, player_id=current_user.id).first()
                if not existing_player_score:
                    new_player_score = PlayerScore(player_id=current_user.id, leaderboard_id=leaderboard.id, elo_rating=100, matches_played=0, matches_won=0, matches_lost=0)
                    db.session.add(new_player_score)
                    db.session.commit()
    return redirect(url_for('views.games'))