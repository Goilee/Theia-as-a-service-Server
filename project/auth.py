# auth.py

from cachecontrol import CacheControl
import requests

from flask import session, abort, redirect, request, Blueprint, render_template, redirect, url_for, flash, current_app

from json import loads

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from .models import User, Role
from . import db
from .config import HOST, PORT


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()
    current_app.logger.info(f'LOGIN: {email} {password} {remember} {user}')

    if not user:
        flash('Пользователь с таким email не найден')
        return redirect(url_for('auth.login'))

    if not check_password_hash(user.password, password):
        flash('Неверный пароль')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    session["email"] = email

    if user.role == Role.ADMIN:
        current_app.logger.info(f'ADMIN')
        return redirect(url_for('admin.user_management'))
    else:
        current_app.logger.info(f'USER')
        return redirect(url_for('main.profile'))


@auth.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == Role.ADMIN:
            return redirect(url_for('admin.user_management'))
        else:
            return redirect(url_for('main.profile'))
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    current_app.logger.info(f'Logout: {session.get("email")}')
    logout_user()
    return redirect(url_for('auth.login'))