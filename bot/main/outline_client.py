import traceback

from django.conf import settings

from outline_vpn.outline_vpn import OutlineVPN
import django_orm
from bot.models import VpnKey
from bot.models import Server
from bot.models import TelegramUser

DEBUG = settings.DEBUG


async def update_keys_data_limit(user: TelegramUser):
    try:
        data = VpnKey.objects.filter(user=user).first().server.script_out
        client = OutlineVPN(api_url=data['apiUrl'], cert_sha256=data['certSha256'])
        if DEBUG: print(data)

        #  Обновляем запись в ключе
        key_id = VpnKey.objects.filter(user=user).first().key_id
        used_bytes = client.get_transferred_data()['bytesTransferredByUserId'][key_id]
        VpnKey.objects.filter(user=user).update(used_bytes=used_bytes)
        if DEBUG: print(key_id, used_bytes)

        #  Обновляем data_limit у пользователя
        data_limit = int(user.data_limit) - int(used_bytes)
        TelegramUser.objects.filter(user_id=user.user_id).update(data_limit=data_limit)
        if DEBUG: print(data_limit)

    except:
        if DEBUG: print(traceback.format_exc())


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
            data_limit = user.data_limit
            data_limit = data_limit
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
            if DEBUG: print(keys_generated, 'keys_generated')
            g = Server.objects.filter(id=server.id).update(keys_generated=keys_generated)
            if DEBUG: print(g, 'g')
        except:
            print(traceback.format_exc())
        return key.access_url
    except:
        print(traceback.format_exc())


async def delete_user_keys(user: TelegramUser) -> bool:
    """
    Delete all vpn-keys associated with user
    :param user: TelegramUser from models
    :return: True if deletion was successful, False otherwise
    """
    if DEBUG: print('deleting all vpn-keys for user', user.id)
    try:
        servers = [x.server.script_out for x in VpnKey.objects.filter(user=user)]
        # servers = [data.script_out for data in Server.objects.all()]
        if DEBUG: print('server data', servers)
        keys = [key.key_id for key in VpnKey.objects.filter(user=user)]
        used_bytes = VpnKey.objects.filter(user=user).first().used_bytes
        data_limit = int(user.data_limit) - int(used_bytes)
        TelegramUser.objects.filter(user_id=user.user_id).update(data_limit=data_limit)
        if DEBUG: print('keys data', keys)
        for data in servers:
            client = OutlineVPN(api_url=data['apiUrl'], cert_sha256=data['certSha256'])
            for key in keys:
                try:
                    if DEBUG: print('Удаляем Ключ :: ', key)
                    client.delete_key(key)
                    keys.remove(key)
                    if DEBUG: print('Ключ Успешно Удалён :: ', key)

                    try:
                        #  Добавляется запись об уменьшении кол-ва сгенерированных ключей на -1
                        keys_generated = Server.objects.filter(script_out=data).first().keys_generated - 1
                        if DEBUG: print(keys_generated, 'keys_generated')
                        Server.objects.filter(script_out=data).update(keys_generated=keys_generated)
                    except:
                        print(traceback.format_exc())

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
