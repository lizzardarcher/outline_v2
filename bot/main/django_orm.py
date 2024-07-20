import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'outline_v2.settings'
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from bot.models import *

user = TelegramUser.objects.get(user_id=5566146968)

l = VpnKey.objects.get(user=user)

print(user, l)
