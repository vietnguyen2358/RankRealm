from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user
from datetime import datetime

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

@views.route('/user-profile')
@login_required
def user_profile():
    owned_games = Game.query.filter_by(owner_id=current_user.id).all()
    return render_template('user_profile.html', user=current_user, owned_games=owned_games)

@views.route('/update-user-profile', methods=['POST'])
@login_required
def update_user_profile():
    current_user.username = request.form.get('username')
    current_user.email = request.form.get('email')
    # Update other user information fields as needed
    db.session.commit()
    return redirect(url_for('views.user_profile'))

@views.route('/add-game', methods=['POST'])
@login_required
def add_game():
    if current_user.is_game_owner:
        title = request.form.get('title')
        description = request.form.get('description')
        release_date_str = request.form.get('release_date')
        release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
        new_game = Game(title=title, description=description, release_date=release_date, owner_id=current_user.id)
        db.session.add(new_game)
        db.session.commit()

        # Create a default leaderboard for the game
        default_leaderboard = Leaderboard(game_id=new_game.id, name="Main Leaderboard")
        db.session.add(default_leaderboard)
        db.session.commit()

    return redirect(url_for('views.user_profile'))


@views.route('/delete-player-score/<int:player_score_id>', methods=['POST'])
@login_required
def delete_player_score(player_score_id):
    player_score = PlayerScore.query.get_or_404(player_score_id)
    if player_score.leaderboard.game.owner_id != current_user.id:
        abort(403)  # Forbidden if the current user is not the game owner

    db.session.delete(player_score)
    db.session.commit()
    return redirect(url_for('views.user_profile'))


# TODO: idk why but this method wont let me delete the game if im logged in. if someone can fix this that would be
#  awesome
@views.route('/delete-game/<int:game_id>', methods=['POST'])
@login_required
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    if game.owner_id != current_user.id:
        abort(403)  # Forbidden if the current user is not the game owner

    # Delete the game and its associated leaderboards and player scores
    leaderboards = Leaderboard.query.filter_by(game_id=game.id).all()
    for leaderboard in leaderboards:
        player_scores = PlayerScore.query.filter_by(leaderboard_id=leaderboard.id).all()
        for player_score in player_scores:
            db.session.delete(player_score)
        db.session.delete(leaderboard)
    db.session.delete(game)
    db.session.commit()

    return redirect(url_for('views.user_profile'))