import asyncio
import logging

from telebot.async_telebot import AsyncTeleBot

import django_orm
from bot.models import TelegramBot
from bot.models import TelegramUser

from bot.main import msg
from bot.main import markup

bot = AsyncTeleBot(TelegramBot.objects.get(pk=1).token)
logging.basicConfig(level=logging.DEBUG)


@bot.message_handler(commands=['start'])
async def start(message):
    if message.chat.type == 'private':
        try:
            TelegramUser.objects.create(user_id=message.from_user.id,
                                        username=message.from_user.username,
                                        first_name=message.from_user.first_name,
                                        last_name=message.from_user.last_name)
        except:
            ...
        await bot.send_message(chat_id=message.chat.id, text=msg.start_message.format(message.from_user.first_name))
        await bot.send_message(chat_id=message.chat.id, text=msg.main_menu)
        await bot.send_message(chat_id=message.chat.id, text=msg.main_menu_choice, reply_markup=markup.start())


@bot.callback_query_handler(func=lambda call: True)
async def callback_query_handlers(call):
    data = call.data.split(':')
    print(data)
    if call.message.chat.type == 'private':

        if 'manage' in data:
            await bot.send_message(call.message.chat.id, msg.avail_location_choice,
                                   reply_markup=markup.get_avail_location())
        elif 'country' in data:
            if TelegramUser.objects.get(user_id=call.message.chat.id).subscription_status:

                if 'netherland' in data:
                    await bot.send_message(call.message.chat.id, msg.key_avail)

                elif 'poland' in data:
                    await bot.send_message(call.message.chat.id, msg.key_avail)

                elif 'kazakhstan' in data:
                    await bot.send_message(call.message.chat.id, msg.key_avail)

                elif 'russia' in data:
                    await bot.send_message(call.message.chat.id, msg.key_avail)
            else:
                await bot.send_message(call.message.chat.id, msg.no_subscription,
                                       reply_markup=markup.get_subscription())
        elif 'account' in data:

            if 'top_up_balance' in data:
                ...
            elif 'buy_subscripton' in data:
                ...
        elif 'profile' in data:
            ...
        elif 'help' in data:
            pass
        elif 'common_info' in data:
            ...


asyncio.run(bot.polling(non_stop=True))
