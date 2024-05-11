from flask import Blueprint, render_template, redirect, url_for, request, abort, flash
from flask_login import login_required, current_user, logout_user
from datetime import datetime

from . import db
from .models import Game, Leaderboard, PlayerScore, User, Event, EventLeaderboard

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
    game_owners = User.query.filter_by(is_game_owner=True).all()
    return render_template('user_profile.html', user=current_user, owned_games=owned_games, game_owners=game_owners)
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

@views.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user = current_user

    # Delete player scores associated with the user
    player_scores = PlayerScore.query.filter_by(player_id=user.id).all()
    for player_score in player_scores:
        db.session.delete(player_score)

    # Delete games owned by the user
    owned_games = Game.query.filter_by(owner_id=user.id).all()
    for game in owned_games:
        leaderboards = Leaderboard.query.filter_by(game_id=game.id).all()
        for leaderboard in leaderboards:
            player_scores = PlayerScore.query.filter_by(leaderboard_id=leaderboard.id).all()
            for player_score in player_scores:
                db.session.delete(player_score)
            db.session.delete(leaderboard)
        db.session.delete(game)

    # Delete the user account
    db.session.delete(user)
    db.session.commit()

    # Log out the user
    logout_user()

    return redirect(url_for('views.home'))

@views.route('/transfer-ownership/<int:game_id>', methods=['POST'])
@login_required
def transfer_ownership(game_id):
    game = Game.query.get_or_404(game_id)
    if game.owner_id != current_user.id:
        abort(403)  # Forbidden if the current user is not the game owner

    new_owner_id = request.form.get('new_owner_id')
    new_owner = User.query.get(new_owner_id)

    if new_owner:
        if new_owner.is_game_owner:
            game.owner_id = new_owner.id
            db.session.commit()
            flash('Ownership transferred successfully.', 'success')
        else:
            flash('The new owner must have the game owner flag.', 'error')
    else:
        flash('User not found.', 'error')

    return redirect(url_for('views.user_profile'))

@views.route('/update-score/<int:game_id>', methods=['POST'])
@login_required
def update_score(game_id):
    game = Game.query.get_or_404(game_id)
    leaderboard = Leaderboard.query.filter_by(game_id=game.id).first()

    if leaderboard:
        player_score = PlayerScore.query.filter_by(leaderboard_id=leaderboard.id, player_id=current_user.id).first()

        if player_score:
            points_scored = int(request.form.get('points_scored'))
            points_against = int(request.form.get('points_against'))

            # Calculate the new ELO rating
            k_factor = 32
            expected_score = 1 / (1 + 10 ** ((points_against - points_scored) / 400))
            actual_score = 1 if points_scored > points_against else 0
            elo_change = k_factor * (actual_score - expected_score)

            new_elo_rating = player_score.elo_rating + elo_change
            new_elo_rating = max(10, min(new_elo_rating, 1500))  # Clamp the ELO rating between 10 and 1500

            player_score.elo_rating = int(new_elo_rating)
            player_score.matches_played += 1

            if points_scored > points_against:
                player_score.matches_won += 1
            else:
                player_score.matches_lost += 1

            db.session.commit()
            flash('Score updated successfully.', 'success')
        else:
            flash('Player score not found.', 'error')
    else:
        flash('Leaderboard not found.', 'error')

    return redirect(url_for('views.games'))

@views.route('/event', methods=['GET'])
def events():
    search_query = request.args.get('q')
    if search_query:
        events = Event.query.filter(Event.title.ilike(f"%{search_query}")).all()
        if not events:
            flash("No events match your search criteria", "warning")
            events = []
    else:
        events = Event.query.all()
    return render_template('event.html', events=events, games=games)

@views.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        game_id = request.form.get('game_id')
        title = request.form.get('title')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%dT%H:%M')

        new_event = Event(game_id=game_id, title=title, owner_id=current_user.id, start_date=start_date, end_date=end_date)
        db.session.add(new_event)
        db.session.commit()

        return redirect(url_for('views.events'))

    games = Game.query.all()
    users = User.query.all()
    return render_template('add_event.html', games=games, users=users)

@views.route('/event/<int:event_id>')
@login_required
def individual_event(event_id):
    event = Event.query.get_or_404(event_id)
    event_leaderboard = EventLeaderboard.query.filter_by(event_id=event_id).all()

    main_leaderboard = Leaderboard.query.filter_by(game_id=event.game_id, name='Main Leaderboard').first()
    eligible_players = [entry.player for entry in main_leaderboard.player_scores]

    return render_template('individual_event.html', event=event, event_leaderboard=event_leaderboard, eligible_players=eligible_players)

@views.route('/add-player-to-event/<int:event_id>', methods=['POST'])
@login_required
def add_player_to_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.owner_id != current_user.id:
        abort(403)  # Forbidden if the current user is not the event owner

    player_id = request.form.get('player_id')

    new_entry = EventLeaderboard(event_id=event_id, player_id=player_id, elo_rating=1000)
    db.session.add(new_entry)
    db.session.commit()

    return redirect(url_for('views.individual_event', event_id=event_id))

@views.route('/remove-player-from-event/<int:event_id>/<int:player_id>', methods=['POST'])
@login_required
def remove_player_from_event(event_id, player_id):
    event = Event.query.get_or_404(event_id)
    if event.owner_id != current_user.id:
        abort(403)  # Forbidden if the current user is not the event owner

    entry = EventLeaderboard.query.filter_by(event_id=event_id, player_id=player_id).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()

    return redirect(url_for('views.individual_event', event_id=event_id))

@views.route('/delete-event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.owner_id != current_user.id:
        abort(403)  # Forbidden if the current user is not the event owner

    db.session.delete(event)
    db.session.commit()

    return redirect(url_for('views.events'))

@views.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')