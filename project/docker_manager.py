from subprocess import Popen, PIPE
from flask import current_app
from flask_login import current_user

from .models import Containers
from . import db
from project.config import HOST, DOCKER_IMAGE, DOCKER_NEW_CLIENT_OUTPUT_SUBSTR, DOCKER_CLIENT_EXITED_OUTPUT_SUBSTR, DOCKER_EXPOSED_PORT


# запускает команду в shell и возвращает вывод
def run_cmd(cmd):
    process = Popen(cmd, stdout=PIPE, shell=True)
    return process.communicate()[0].decode('utf-8')


# запускает контейнер на случайном порту и возвращает вывод
def start_container(id):
    result = run_cmd(f'docker start {id}')
    current_app.logger.info(f'Started container {result[:-1]}')
    return result


# создаёт контейнер RIDE и добавляет в БД, возвращает id
def create_container():
    id = run_cmd(f'docker create --ip={HOST} --publish 3000 {DOCKER_IMAGE}')[:12]
    name = run_cmd('docker ps -a --filter "id=' + id + '" --format "{{.Names}}"')[:-1]
    current_app.logger.info(f'Created container {name} ({id})')
    
    new_container = Containers(id=id, user_id=current_user.id, container_name=name)
    db.session.add(new_container)
    db.session.commit()
    current_app.logger.info(f'Added new container {new_container.container_name} ({new_container.id}) to DB')
    
    return id


# останавливает контейнер и возвращает вывод команды
def stop_container(id):
    result = run_cmd(f'docker stop {id}')
    current_app.logger.info(f'Stopped container: {result[:-1]}')
    return result


# удаляет контейнер из докера и из БД, возвращает вывод докер команды
def force_remove_container(id):
    result = run_cmd(f'docker rm -f {id}')[:-1]
    current_app.logger.info(f'Force removed container: {result}')
    
    Containers.query.filter_by(id=id).delete()
    db.session.commit()
    current_app.logger.info(f'Deleted container {id} from DB')
    
    return result


# возвращает число строк в логах контейнера, содержащих подстроку substr
# если вдруг утилита wc вернёт не число, выбросится исключение с выводом wc
def number_of_log_lines(container, substr):
    result = run_cmd(f'''docker logs {container} 2>&1 | grep -n "{substr}" | wc -l''')
    try:
        return int(result)
    except ValueError:
    	raise Exception(f'"wc -l" returned: {result}')


# возвращает список айднишников контейнеров
def get_containers():
    return run_cmd(f'docker ps -q --filter "ancestor={DOCKER_IMAGE}"').splitlines()


# останавливает запущенные контейнеры, из которых вышел юзер (или все, если параметр True)
def stop_containers(stop_all = False):
    current_app.logger.info(f'Stopping containers (stop_all={stop_all})...')
    for container in get_containers():
        to_stop = stop_all
        if not to_stop:
            clients_entered = number_of_log_lines(container, DOCKER_NEW_CLIENT_OUTPUT_SUBSTR)
            clients_exited = number_of_log_lines(container, DOCKER_CLIENT_EXITED_OUTPUT_SUBSTR)
            current_app.logger.info(f'Container {container}: entered {clients_entered}, exited {clients_exited}')
            to_stop = clients_exited >= clients_entered
        if to_stop:
            stop_container(container)


# возвращает назначенный контейнеру порт (None, если такой контейнер не запущен)
def get_container_port(id):
    result = run_cmd(f'docker port {id[:12]} {DOCKER_EXPOSED_PORT}')
    try:
        return int(result.splitlines()[0][8:])
    except ValueError:
        current_app.logger.error(f'docker port returned: {result[:-1]}')
        return None


def get_URL(id):
    port = get_container_port(id)
    URL = f'http://{HOST}:{port}'
    return URL

