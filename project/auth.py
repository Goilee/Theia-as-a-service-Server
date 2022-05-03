# auth.py

from cachecontrol import CacheControl
import requests

from flask import session, abort, redirect, request, Blueprint, render_template, redirect, url_for, flash, current_app

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests

from json import loads

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

from .models import Users
from . import db
from .config import CLIENT_SECRET_FILE, HOST, PORT


auth = Blueprint('auth', __name__)

with open (CLIENT_SECRET_FILE, 'r') as f:
    GOOGLE_CLIENT_ID = loads(f.read())['web']['client_id']

flow = Flow.from_client_secrets_file(
    client_secrets_file=CLIENT_SECRET_FILE,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri=f'http://{HOST}:{PORT}/callback'
)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = Users.query.filter_by(email=email).first()
    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        current_app.logger.info(f'Logging failed for user {email}')
        return redirect(url_for('auth.login'))  # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    session["email"] = email
    current_app.logger.info(f'Logging succeeded for user {email}')
    return redirect(url_for('main.profile'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = Users.query.filter_by(
        email=email).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        current_app.logger.info(f'Signup failed for user {email}')
        return redirect(url_for('auth.signup'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = Users(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    current_app.logger.info(f'Signup succeeded for user {email}')
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    current_app.logger.info(f'Logout: {session.get("email")}')
    logout_user()
    return redirect(url_for('main.index'))


########################################################################################################################

@auth.route("/google_login")
def google_login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


# callback from google
@auth.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        current_app.logger.warning(f'State does not match: state {session["state"]}, request {request.args["state"]}')
        abort(500)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["email"] = id_info.get("email")
    session["name"] = id_info.get("name")

    user = Users.query.filter_by(email=session.get("email")).first()

    if user:
        login_user(user)
        current_app.logger.info(f'Google login succeeded for user {session.get("email")}')
        return redirect(url_for('main.profile'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = Users(email=session.get("email"), name=session.get("name"))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    current_app.logger.info(f'Signup via google login: new user {session.get("email")}')
    
    user = Users.query.filter_by(email=session.get("email")).first()
    login_user(user)
    current_app.logger.info(f'Google login succeeded for user {session.get("email")}')
    return redirect(url_for('main.profile'))
