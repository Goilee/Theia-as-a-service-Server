import logging
from argparse import ArgumentParser
from threading import Thread
from os import _exit

try:
    from apscheduler.schedulers.blocking import BlockingScheduler
except ModuleNotFoundError:
    print("Ошибка: APScheduler не установлен. Установите его командой: pip install apscheduler")
    _exit(1)

from project.config import CONFIG_FILE, CLEANER_TIME_INTERVAL_IN_SECONDS, HOST, PORT
from project import app
from project.docker_manager import stop_containers

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SETTINGS_FILE = 'config.ini'

parser = ArgumentParser(description=f'Docker application server. Look for parameters in the {CONFIG_FILE}.')
parser.add_argument('-d', '--debug', help='Run in debug mode', action='store_const', const=True, default=False)
args = parser.parse_args()

# Создание планировщика
scheduler = BlockingScheduler()
scheduler.add_job(stop_containers, 'interval', seconds=CLEANER_TIME_INTERVAL_IN_SECONDS)

def run_scheduler():
    try:
        scheduler.start()
    except Exception as e:
        logger.error(f"Ошибка в планировщике: {e}")
    finally:
        logger.info("Планировщик остановлен.")

# Запуск планировщика в отдельном потоке (daemon=True, чтобы завершался с программой)
cleaner_thread = Thread(target=run_scheduler, daemon=True)
cleaner_thread.start()

with app.app_context():
    try:
        logger.info(f"Запуск сервера на {HOST}:{PORT} (debug={args.debug})")
        app.run(host=HOST, port=PORT, debug=args.debug)
    except KeyboardInterrupt:
        logger.info("Остановка сервера (Ctrl+C)")
    except Exception as e:
        logger.critical(f"Критическая ошибка сервера: {e}")
    finally:
        logger.info("Остановка всех контейнеров...")
        stop_containers(stop_all=True)
        scheduler.shutdown(wait=False)  # Корректно останавливаем планировщик
        _exit(0)  # Полное завершение программы
