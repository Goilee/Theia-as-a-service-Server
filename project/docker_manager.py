from subprocess import Popen, PIPE
from .models import Containers
from . import db


# запускает команду в shell и возвращает вывод
def run_cmd(cmd):
    process = Popen(cmd, stdout=PIPE, shell=True)
    return process.communicate()[0].decode('utf-8')


def start_container(id):
    result = run_cmd(f'docker start {id}')[:-1]
    print(f'Started: {result}')
    return result


# запускает контейнер RIDE на случайном порту и возвращает кортеж (ip, port)
def run_container():
    host = '127.0.0.1'
    container = run_cmd(f'docker run --ip={host} --detach --publish 3000 ride')[:-1]
    port = int(run_cmd(
        "docker inspect -f '{{ (index (index .NetworkSettings.Ports \"3000/tcp\") 0).HostPort }}' " + container))
    print(f'Started RIDE container (id={container}) on ({host},{port})')
    container = container[:12]
    name = run_cmd('docker ps --filter "id=' + container + '" --format "{{.Names}}"')
    print(container, name)
    return host, port, container, name


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
    result = run_cmd('docker ps -q --filter "ancestor=ride"')
    return result.splitlines()


# удаляет запущенные контейнеры, из которых вышел юзер (или все, если параметр True)
def clean_containers(cleanAll=False):
    for container in get_running_containers():
        clientEnter = find_last_line_in_logs(container, "Set client")
        clientExit = find_last_line_in_logs(container, "All contributions have been stopped")
        print(f'Container {container}: entered {clientEnter}, exited {clientExit}')
        if clientExit > clientEnter:
            # force_remove_container(container)
            stop_container(container)
        if cleanAll:
            # TODO: сделать фильтр на остановленные контейнеры тоже!
            force_remove_container(container)


# фильтр на запущенные порты
def get_running_ports(id):
    result = run_cmd(f'docker port {id[:12]} 3000')
    print(result.splitlines()[1][3:])
    return result.splitlines()[1][3:]


def get_URL(id):
    port = get_running_ports(id)
    URL = f'http://127.0.0.1:{port}/#/RIDE-workspaces'
    print(URL)
    return URL

