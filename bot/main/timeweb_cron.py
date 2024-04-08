import time

import django_orm
from bot.models import GlobalSettings
from bot.models import Server
from bot.models import Country
from bot.main.timeweb.timeweb import TimeWeb

timeweb_token = GlobalSettings.objects.get(pk=1).time_web_api_key
cloud_init = GlobalSettings.objects.get(pk=1).cloud_init
os_id = GlobalSettings.objects.get(pk=1).os_id
software_id = GlobalSettings.objects.get(pk=1).software_id
servers = Server.objects.all()
countries = Country.objects.all()

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


def init_servers(countries: Country, headers: dict, json_data: dict, token: str):

    client = TimeWeb(token=token, headers=headers)

    for country in countries:
        print(country.name, country.preset_id)
        json_data['preset_id'] = country.preset_id

        server = Server.objects.filter(country=country)
        if not server.exists():

            # Создание сервера
            server = client.create_server(json_data=json_data)
            print(server)
            print(server)
        else:
            print(server, 'is active')



init_servers(countries=countries, headers=headers, json_data=json_data, token=timeweb_token)