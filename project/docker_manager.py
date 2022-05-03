from subprocess import Popen, PIPE
from .models import Containers

from . import db
from project.config import HOST, DOCKER_IMAGE, DOCKER_NEW_CLIENT_OUTPUT_SUBSTR, DOCKER_CLIENT_EXITED_OUTPUT_SUBSTR, DOCKER_EXPOSED_PORT


# запускает команду в shell и возвращает вывод
def run_cmd(cmd):
    process = Popen(cmd, stdout=PIPE, shell=True)
    return process.communicate()[0].decode('utf-8')


def start_container(id):
    result = run_cmd(f'docker start {id}')[:-1]
    print(f'Started: {result}')
    return result


# запускает контейнер RIDE на случайном порту и возвращает кортеж (ip, port, id, name)
def run_container():
    container = run_cmd(f'docker run --ip={HOST} --detach --publish 3000 ride')[:12]
    port = get_container_port(container)
    name = run_cmd('docker ps --filter "id=' + container + '" --format "{{.Names}}"')
    print(f'Started container {name} (id={container}) on ({HOST},{port})')
    return HOST, port, container, name


# останавливает контейнер и возвращает вывод команды
def stop_container(id):
    result = run_cmd(f'docker stop {id}')[:-1]
    print(f'Stopped: {result}')
    return result


# удаляет контейнер и возвращает вывод команды
def force_remove_container(id):
    result = run_cmd(f'docker rm -f {id}')[:-1]
    Containers.query.filter_by(id=id).delete()
    db.session.commit()
    print(f'Force removed: {result}')
    return result


# возвращает номер последней строки, содержащей подстроку line (-1 при отсутствии)
def find_last_line_in_logs(container, substr):
    result = run_cmd(f'''docker logs {container} 2>&1 | grep -n "{substr}" | tail --lines=1''')
    try:
        lineNumber = int(result[0:result.index(':')])
        return lineNumber
    except ValueError:
        return -1


# возвращает список айднишников запущенных контейнеров
def get_running_containers():
    result = run_cmd(f'docker ps -q --filter "ancestor={DOCKER_IMAGE}"')
    return result.splitlines()


# удаляет запущенные контейнеры, из которых вышел юзер (или все, если параметр True)
def clean_containers(cleanAll=False):
    for container in get_running_containers():
        clientEnter = find_last_line_in_logs(container, DOCKER_NEW_CLIENT_OUTPUT_SUBSTR)
        clientExit = find_last_line_in_logs(container, DOCKER_CLIENT_EXITED_OUTPUT_SUBSTR)
        print(f'Container {container}: entered {clientEnter}, exited {clientExit}')
        if clientExit > clientEnter:
            # force_remove_container(container)
            stop_container(container)
        if cleanAll:
            # TODO: сделать фильтр на остановленные контейнеры тоже!
            force_remove_container(container)


# возвращает назначенный контейнеру порт (None, если такой контейнер не запущен)
def get_container_port(id):
    result = run_cmd(f'docker port {id[:12]} {DOCKER_EXPOSED_PORT}')
    try:
        return int(result.splitlines()[0][8:])
    except ValueError:
        return None


def get_URL(id):
    port = get_container_port(id)
    URL = f'http://{HOST}:{port}'
    print(URL)
    return URL

