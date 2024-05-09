import re
from flask import Blueprint, flash, redirect, render_template, url_for, request, session
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Game, Leaderboard, PlayerScore, Event, db
from datetime import datetime

auth = Blueprint('auth', __name__)

# ... (existing user authentication routes)

@auth.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'ADMINPASS':  # Replace with your desired admin password
            session['admin_logged_in'] = True
            return redirect(url_for('auth.admin_dashboard'))
        else:
            flash('Invalid password. Please try again.', 'error')
            return redirect(url_for('auth.admin_login'))
    return render_template('admin_login.html')

@auth.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('auth.admin_login'))

@auth.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    users = User.query.all()
    games = Game.query.all()
    leaderboards = Leaderboard.query.all()
    player_scores = PlayerScore.query.all()
    events = Event.query.all()
    return render_template('admin_dashboard.html', users=users, games=games, leaderboards=leaderboards, player_scores=player_scores, events=events)

@auth.route('/add_user', methods=['POST'])
def add_user():
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    is_game_owner = True if request.form.get('is_game_owner') else False
    new_user = User(username=username, email=email, is_game_owner=is_game_owner)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.is_game_owner = True if request.form.get('is_game_owner') else False
        db.session.commit()
        return redirect(url_for('auth.admin_dashboard'))
    return render_template('edit_user.html', user=user)

@auth.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/add_game', methods=['POST'])
def add_game():
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    title = request.form.get('title')
    description = request.form.get('description')
    release_date = datetime.strptime(request.form.get('release_date'), '%Y-%m-%d')
    owner_id = request.form.get('owner_id')
    new_game = Game(title=title, description=description, release_date=release_date, owner_id=owner_id)
    db.session.add(new_game)
    db.session.commit()
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/edit_game/<int:game_id>', methods=['GET', 'POST'])
def edit_game(game_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    game = Game.query.get_or_404(game_id)
    users = User.query.all()
    if request.method == 'POST':
        game.title = request.form.get('title')
        game.description = request.form.get('description')
        game.release_date = datetime.strptime(request.form.get('release_date'), '%Y-%m-%d')
        game.owner_id = request.form.get('owner_id')
        db.session.commit()
        return redirect(url_for('auth.admin_dashboard'))
    return render_template('edit_game.html', game=game, users=users)

@auth.route('/delete_game/<int:game_id>')
def delete_game(game_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    game = Game.query.get_or_404(game_id)
    db.session.delete(game)
    db.session.commit()
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/add_leaderboard', methods=['POST'])
def add_leaderboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    game_id = request.form.get('game_id')
    new_leaderboard = Leaderboard(game_id=game_id)
    db.session.add(new_leaderboard)
    db.session.commit()
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/edit_leaderboard/<int:leaderboard_id>', methods=['GET', 'POST'])
def edit_leaderboard(leaderboard_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    leaderboard = Leaderboard.query.get_or_404(leaderboard_id)
    games = Game.query.all()
    if request.method == 'POST':
        leaderboard.game_id = request.form.get('game_id')
        db.session.commit()
        return redirect(url_for('auth.admin_dashboard'))
    return render_template('edit_leaderboard.html', leaderboard=leaderboard, games=games)

@auth.route('/delete_leaderboard/<int:leaderboard_id>')
def delete_leaderboard(leaderboard_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    leaderboard = Leaderboard.query.get_or_404(leaderboard_id)
    db.session.delete(leaderboard)
    db.session.commit()
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/add_player_score', methods=['POST'])
def add_player_score():
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    player_id = request.form.get('player_id')
    game_id = request.form.get('game_id')
    elo_rating = request.form.get('elo_rating')
    matches_played = request.form.get('matches_played')
    matches_won = request.form.get('matches_won')
    matches_lost = request.form.get('matches_lost')
    new_player_score = PlayerScore(player_id=player_id, game_id=game_id, elo_rating=elo_rating, matches_played=matches_played, matches_won=matches_won, matches_lost=matches_lost)
    db.session.add(new_player_score)
    db.session.commit()
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/edit_player_score/<int:player_score_id>', methods=['GET', 'POST'])
def edit_player_score(player_score_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    player_score = PlayerScore.query.get_or_404(player_score_id)
    users = User.query.all()
    games = Game.query.all()
    if request.method == 'POST':
        player_score.player_id = request.form.get('player_id')
        player_score.game_id = request.form.get('game_id')
        player_score.elo_rating = request.form.get('elo_rating')
        player_score.matches_played = request.form.get('matches_played')
        player_score.matches_won = request.form.get('matches_won')
        player_score.matches_lost = request.form.get('matches_lost')
        db.session.commit()
        return redirect(url_for('auth.admin_dashboard'))
    return render_template('edit_player_score.html', player_score=player_score, users=users, games=games)

@auth.route('/delete_player_score/<int:player_score_id>')
def delete_player_score(player_score_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    player_score = PlayerScore.query.get_or_404(player_score_id)
    db.session.delete(player_score)
    db.session.commit()
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/add_event', methods=['POST'])
def add_event():
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    game_id = request.form.get('game_id')
    host_id = request.form.get('host_id')
    player_id = request.form.get('player_id')
    start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%dT%H:%M')
    end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%dT%H:%M')
    new_event = Event(game_id=game_id, host_id=host_id, player_id=player_id, start_date=start_date, end_date=end_date)
    db.session.add(new_event)
    db.session.commit()
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    event = Event.query.get_or_404(event_id)
    users = User.query.all()
    games = Game.query.all()
    if request.method == 'POST':
        event.game_id = request.form.get('game_id')
        event.host_id = request.form.get('host_id')
        event.player_id = request.form.get('player_id')
        event.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%dT%H:%M')
        event.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%dT%H:%M')
        db.session.commit()
        return redirect(url_for('auth.admin_dashboard'))
    return render_template('edit_event.html', event=event, users=users, games=games)

@auth.route('/delete_event/<int:event_id>')
def delete_event(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.admin_login'))
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('auth.admin_dashboard'))