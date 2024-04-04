from outline_vpn.outline_vpn import OutlineVPN
import django_orm
from bot.models import VpnKey
from bot.models import Server
from bot.models import TelegramUser

data = {"apiUrl": "https://213.171.12.240:61550/pyDHk6tgZk6bnd321tkgXg",
        "certSha256": "CAD7DB50513F6F74FCD016D0BC7DC30C24645803024EA5AD5353BF509F48E73B"}

# Setup the access with the API URL (Use the one provided to you after the server setup)

# Get all access URLs on the server
# for key in client.get_keys():
#     print(key)


def create_new_key(server: Server, user: TelegramUser) -> str:
    data = dict(server.script_out)
    client = OutlineVPN(api_url=data['apiUrl'], cert_sha256=data['certSha256'])
    key = client.create_key()
    VpnKey.objects.create(server=server, user=user)
    return key.access_url

print(create_new_key(server=Server.objects.all()[0], user=TelegramUser.objects.all()[0]))
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
