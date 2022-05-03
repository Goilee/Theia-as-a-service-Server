# main.py

from flask import Blueprint, render_template, request, session, current_app, flash
from flask_login import current_user, login_required

from .docker_manager import create_container, force_remove_container, get_URL, start_container
from . import db
from .models import Users, Containers
from .config import DOCKER_WAIT_TIME_IN_SECONDS

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/help')
def help():
    return render_template('help.html')


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        data = request.form.getlist('chkbox')

        if 'rename_btn' in request.form:
            rnm = Users.query.filter_by(email=session.get("email")).first().cont
            for c in rnm:
                cont_name = request.form.get(f'cont_name{c.id}')
                
                container = Containers.query.filter_by(id=c.id).first()
                old_name = container.container_name
                container.container_name = cont_name
                db.session.commit()
                current_app.logger.info(f'Renamed container id={container.id}: old name "{old_name}", new name "{container.container_name}"')

        elif 'create_btn' in request.form:
            create_container()

        elif 'delete_btn' in request.form:
            for id in data:
                force_remove_container(id)

        elif 'share_btn' in request.form:
            for id in data:
                URL = get_URL(id)
                flash('Be careful! Everyone will be able to connect to the container using your link!')
                flash(f'Your link: {URL}')

        elif 'run_btn' in request.form:
            for id in data:
                start_container(id)
                URL = get_URL(id)
                return render_template('loader.html'), {"Refresh": f"{DOCKER_WAIT_TIME_IN_SECONDS}; url={URL}"}

    info = []
    try:
        info = Users.query.filter_by(email=session.get("email")).first().cont
    except Exception as e:
        current_app.logger.error(e)

    username = current_user.name
    return render_template('profile.html', name=username, list=info)
