from outline_vpn.outline_vpn import OutlineVPN
import django_orm
from bot.models import VpnKey
from bot.models import Server
from bot.models import TelegramUser
from bot.models import GlobalSettings


# Setup the access with the API URL (Use the one provided to you after the server setup)

# Get all access URLs on the server
# for key in client.get_keys():
#     print(key)
'''
1GB = 1024 * 1024 * 1024
'''

def create_new_key(server: Server, user: TelegramUser) -> str:
    data_limit = GlobalSettings.objects.all()[0].data_limit
    data_limit = data_limit * 1024 * 1024 * 1024
    data = dict(server.script_out)
    client = OutlineVPN(api_url=data['apiUrl'], cert_sha256=data['certSha256'])
    key = client.create_key(
        key_id=f'{str(user.user_id)}:{str(server.id)}',
        name=f'{str(user.user_id)}+ {server.ip_address}',
        data_limit=data_limit
    )
    VpnKey.objects.create(
        server=server,
        user=user,
        key_id=f'{key.key_id}:{server.ip_address}',
        name=key.name,
        password=key.password,
        port=key.port,
        method=key.method,
        access_url=key.access_url,
        used_bytes=key.used_bytes,
        data_limit=key.data_limit
    )
    return key.access_url

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
