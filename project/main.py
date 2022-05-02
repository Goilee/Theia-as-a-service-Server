# main.py
import datetime

from .docker_manager import run_container, force_remove_container, get_URL, stop_container, start_container
from flask import Blueprint, render_template, request, session, abort, current_app, flash
from flask_login import current_user, login_required
from . import db
from .models import Users, Containers

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
        print("post")
        data = request.form.getlist('chkbox')

        if 'rename_btn' in request.form:
            print(request.form['rename_btn'])
            rnm = Users.query.filter_by(email=session.get("email")).first().cont
            for c in rnm:
                cont_name = request.form.get(f'cont_name{c.id}')
                print(c.id, cont_name)
                container = Containers.query.filter_by(id=c.id).first()
                print(container)

                print(cont_name)
                container.container_name = cont_name
                db.session.commit()

        elif 'create_btn' in request.form:
            print(request.form['create_btn'])
            (host, port, container, name) = run_container()
            print(current_user.id)
            print(container)
            new_container = Containers(id=container, user_id=current_user.id, container_name=name)
            print(name)

            # add the new container to the database
            db.session.add(new_container)
            db.session.commit()

            return render_template('loader.html'), {"Refresh": f"3; url=http://{host}:{port}"}

        elif 'delete_btn' in request.form:
            print(request.form['delete_btn'])
            for id in data:
                print(id)
                force_remove_container(id)

        elif 'share_btn' in request.form:
            print(request.form['share_btn'])
            for id in data:
                print(id)
                URL = get_URL(id)
                flash('Be careful! Everyone will be able to connect to the container using your link!')
                flash(f'Your link: {URL}')

        elif 'run_btn' in request.form:
            print(request.form['run_btn'])
            for id in data:
                print(id)
                start_container(id)
                URL = get_URL(id)
                return render_template('loader.html'), {"Refresh": f"3; url={URL}"}

    info = []
    try:
        info = Users.query.filter_by(email=session.get("email")).first().cont
    except:
        print("Error")

    username = current_user.name
    return render_template('profile.html', name=username, list=info)
