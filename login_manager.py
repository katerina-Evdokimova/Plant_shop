from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app import app
from data import db_session
from data.users import User
from flask import flash, redirect, url_for, request

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    next_page = request.args.get('next')
    flash('Вы вышли из системы.')
    return redirect(next_page or url_for('login'))