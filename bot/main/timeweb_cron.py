import sys
import time
import traceback
from datetime import date
import logging
from logging.handlers import RotatingFileHandler

import paramiko
from django.conf import settings

import django_orm
from bot.models import GlobalSettings
from bot.models import Server
from bot.models import Country
from bot.main.timeweb.timeweb import TimeWeb

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname) -8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y.%m.%d %I:%M:%S',
    handlers=[
        RotatingFileHandler(filename='log/tw_log.log', maxBytes=1024*1024, backupCount=5),
        # TimedRotatingFileHandler(filename='log/tw_log.log', when='D', interval=1, backupCount=5),
        logging.StreamHandler(stream=sys.stderr)
              ],
)
DEBUG = settings.DEBUG



def find_dict_item(obj, key):
    """
    Find a key in a dictionary and return its value.
    :param obj:
    :param key:
    :return:
    """
    if key in obj:
        return obj[key]
    for k, v in obj.items():
        if isinstance(v, dict):
            item = find_dict_item(v, key)
            if item is not None:
                return item


def init_servers(countries: Country, headers: dict, json_data: dict, token: str):
    """
    Первичная установка и настройка серверов.
    :param countries: Coutnry from models
    :param headers: dict headers
    :param json_data: dict json data
    :param token: TimeWeb public API token
    """
    client = TimeWeb(token=token, headers=headers)
    for country in countries:
        json_data['preset_id'] = country.preset_id
        json_data['name'] = f'{country.name}-{country.preset_id}-{str(date.today())}'
        server_obj = Server.objects.filter(country=country)
        if not server_obj.exists():
            logger.info(f'{server_obj}, {country.name}, {country.preset_id}')
            """
            ### Создание сервера
            """
            logger.info(f'Начало создания сервера для {country.name} {country.preset_id} ...')
            server_creating_status = True
            init_server = client.create_server(json_data=json_data)
            time.sleep(300)

            server_id = init_server['server']['id']
            logger.info(f'Cервер для {country.name} {country.preset_id} создан успешно!')

            while server_creating_status:
                try:
                    server = client.get_server(server_id=server_id)
                    logger.info(server.__str__())
                    if country.name != 'russia':
                        ip = server['server']['networks'][0]['ips'][0]['ip']
                    else:
                        ip = server['server']['networks'][0]['ips'][1]['ip']
                    password = server['server']['root_pass']
                    if ip and password:
                        server_creating_status = False
                        break
                except Exception as e:
                    time.sleep(15)
                    logger.error(traceback.format_exc())

            # доступ по SSH и получение скрипта для outline VPN

            logger.info(f'Подключаемся к новому серверу по SSH root@{ip} pwd:{password} port:22')
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=ip, username='root', password=password, port=22)
                stdin, stdout, stderr = ssh.exec_command('cd .. && cat configfile.txt')
                out = stdout.read() + stderr.read()
                logger.info(out.__str__())
                open('configfile.txt', 'w').write(out.__str__())
                ssh.close()
            except Exception as e:
                logger.error(traceback.format_exc())
            time.sleep(60)
            logger.info('Подключение прошло успешно! Файл configfile.txt обновлён')

            # Получение apiUrl и certSha256

            logger.info('Чтение данных из configfile.txt')
            data = dict()
            with open('configfile.txt', 'r') as config_file:
                config = config_file.read()
                for line in config.split(' '):
                    if 'interface' in line:
                        raw = line.split('{')[1].split('}')[0].split(',')
                        data['apiUrl'] = raw[0].split('":"')[-1].replace("'", "").replace('"', '')
                        data['certSha256'] = raw[1].split(':')[-1].replace("'", "").replace('"', '')

            logger.info(f'Данные их configfile.txt получены {str(data)}')
            Server.objects.create(
                id=server_id,
                hosting='TimeWeb',
                ip_address=ip,
                user='root',
                password=password,
                configuration=str(server),
                rental_price=0,
                max_keys=100,
                keys_generated=0,
                is_active=True,
                country=country,
                script_out=data
            )
            logger.info(f'Новый объект Server создан {Server.objects.get(id=server_id)}')
        else:
            logger.info(f'{server_obj} is active')


timeweb_token = GlobalSettings.objects.get(pk=1).time_web_api_key
# cloud_init = GlobalSettings.objects.get(pk=1).cloud_init
cloud_init = '#!/bin/sh\ntouch configfile.txt\nbash -c "$(wget -qO- https://raw.githubusercontent.com/Jigsaw-Code/outline-server/master/src/server_manager/install_scripts/install_server.sh) > configfile.txt"'
os_id = GlobalSettings.objects.get(pk=1).os_id
software_id = GlobalSettings.objects.get(pk=1).software_id
servers = Server.objects.all()
countries = Country.objects.filter(is_active=True)

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {timeweb_token}',
}

json_data = {  # for creating servers
    'is_ddos_guard': False,
    'os_id': os_id,  # Ubuntu 22.04
    'software_id': software_id,  # Docker
    'bandwidth': 200,
    'comment': 'comment',
    'name': 'outline_ru_1',
    'cloud_init': cloud_init,
    'preset_id': 'preset_id',
    'is_local_network': False,
}

if __name__ == '__main__':
    init_servers(countries=countries, headers=headers, json_data=json_data, token=timeweb_token)
