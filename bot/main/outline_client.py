import traceback

from outline_vpn.outline_vpn import OutlineVPN
import django_orm
from bot.models import VpnKey
from bot.models import Server
from bot.models import TelegramUser
from bot.models import GlobalSettings


# Get all access URLs on the server
# for key in client.get_keys():
#     print(key)


async def create_new_key(server: Server, user: TelegramUser) -> str:
    try:
        """
        Создать новый vpn ключ
        :param server: Server from models
        :param user: TelegramUser from models
        :return: access_url
        """
        data_limit = None
        try:
            data_limit = GlobalSettings.objects.all()[0].data_limit
            data_limit = data_limit * 1024 * 1024 * 1024
        except:
            print('no data_limit provided')
        data = dict(server.script_out)
        client = OutlineVPN(api_url=data['apiUrl'], cert_sha256=data['certSha256'])
        key = client.create_key(
            key_id=f'{str(user.user_id)}:{str(server.id)}',
            name=f'{str(user.user_id)}:{server.ip_address}',
            data_limit=data_limit
        )
        VpnKey.objects.create(
            server=server,
            user=user,
            key_id=f'{key.key_id}',
            name=key.name,
            password=key.password,
            port=key.port,
            method=key.method,
            access_url=key.access_url,
            used_bytes=key.used_bytes,
            data_limit=key.data_limit
        )
        """
        Добавляется запись об увеличении кол-ва сгенерированных ключей на +1
        """
        try:
            keys_generated = Server.objects.filter(id=server.id).first().keys_generated + 1
            print(keys_generated, 'keys_generated')
            g = Server.objects.filter(id=server.id).update(keys_generated=keys_generated)
            print(g, 'g')
        except:
            print(traceback.format_exc())
        return key.access_url
    except:
        print(traceback.format_exc())


# todo решить вопрос с большим количеством серверов идёт запрос на удаление по всем серверам
# todo нужно сделать проходжение только по тем серверам, где имеются ключи для удаления
async def delete_all_keys(user: TelegramUser) -> bool:
    """
    Delete all vpn-keys associated with user
    :param user: TelegramUser from models
    :return: True if deletion was successful, False otherwise
    """
    print('deleting all vpn-keys for user', user.id )
    try:
        servers = [data.script_out for data in Server.objects.all()]
        print('server data', servers)
        keys = [key.key_id for key in VpnKey.objects.filter(user=user)]
        print('keys data', keys)
        for data in servers:
            client = OutlineVPN(api_url=data['apiUrl'], cert_sha256=data['certSha256'])
            for key in keys:
                try:
                    print('Удаляем Ключ :: ', key)
                    client.delete_key(key)
                    keys.remove(key)
                    print('Ключ Успешно Удалён :: ', key)
                except:
                    ...
        VpnKey.objects.filter(user=user).delete()
        return True
    except Exception as e:
        print(traceback.format_exc())
        return False


# Create a new key
# new_key = client.create_key()
# print(new_key)
# Rename it
# client.rename_key(new_key.key_id, "new_key")

# Delete it
# client.delete_key(new_key.key_id)

# Set a monthly data limit for a key (20MB)
# client.add_data_limit(new_key.key_id, 1000 * 1000 * 20)

# Remove the data limit
# client.delete_data_limit(new_key.key_id)
