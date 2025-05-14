# main.py

from flask import Blueprint, render_template, request, session, current_app, flash, url_for, redirect
from flask_login import current_user, login_required

from .docker_manager import create_container, force_remove_container, get_URL, start_container
from . import db
from .models import ContainerType, Container, UserContainer
from .config import DOCKER_WAIT_TIME_IN_SECONDS, HOST

main = Blueprint('main', __name__)


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    username = current_user.name

    if request.method == 'POST' and 'run_btn' in request.form:
        container_id = request.form.get('container_id')

        # Проверяем, есть ли связь между текущим пользователем и контейнером
        user_container = UserContainer.query.filter_by(user_id=current_user.id, container_id=container_id).first()

        if user_container:
            # Если контейнер найден, запускаем его
            start_container(container_id)
            URL = get_URL(container_id, username)
            return render_template('loader.html', redirect_url=URL, delay=DOCKER_WAIT_TIME_IN_SECONDS)

    # Получаем контейнеры пользователя через таблицу UserContainer
    containers = [uc.container for uc in current_user.container_links]

    return render_template('profile.html',
                           name=username,
                           list=containers)

@main.route('/access/<container_name>')
@login_required
def access_container(container_name):
    current_app.logger.info(f"Access request for container: {container_name} from user: {current_user.name}")
    container = Container.query.filter_by(container_name=container_name).first_or_404()

    # Проверяем, есть ли у пользователя доступ к контейнеру
    link = UserContainer.query.filter_by(user_id=current_user.id, container_id=container.id).first()
    current_app.logger.info(f"Acc {current_user.id} {container.id}")
    if not link:
        flash("Access denied", "danger")
        return redirect(url_for('main.profile'))

    proxy_url = f"http://{HOST}/proxy/{container.container_name}/"
    current_app.logger.info(f"{proxy_url}")
    return redirect(proxy_url)


@main.route('/access/guest-container')
def guest_access():
    """Специальный маршрут для гостевого доступа без аутентификации"""
    container = Container.query.filter_by(container_type=ContainerType.GUEST).first_or_404()
    start_container(container.id)
    proxy_url = f"http://{HOST}/{container.container_name}/"
    current_app.logger.info(f"{proxy_url}")
    return redirect(proxy_url)
