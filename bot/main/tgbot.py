import asyncio


from telebot.async_telebot import AsyncTeleBot

import django_orm
from apps.bot.models import *
# from apps.bot.main import callback_handler
# from apps.bot.main import message_handler
# from apps.bot.main import msg
# from apps.bot.main import markup


BOT_TOKEN = TelegramBot.objects.get(pk=1).token
# bot = AsyncTeleBot(BOT_TOKEN)
# bot = AsyncTeleBot('7128191998:AAFiI3d0dH_IqSONVRIqHfViTzqrOAcOlho')


# asyncio.run(bot.polling(non_stop=True))
