import asyncio
import logging

from telebot.async_telebot import AsyncTeleBot

import django_orm
from bot.models import TelegramBot
from bot.models import TelegramUser
from bot.models import VpnKey
from bot.models import Server

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
    user = TelegramUser.objects.get(user_id=call.message.chat.id)
    print(data)
    if call.message.chat.type == 'private':

        if 'manage' in data:
            await bot.send_message(call.message.chat.id, msg.avail_location_choice,
                                   reply_markup=markup.get_avail_location())
        elif 'country' in data:
            if user.subscription_status:
                keys = VpnKey.objects.filter(user=user)
                countries = [x.server.country.name for x in keys]
                print(keys)
                print(countries)

                if 'netherland' in data:
                    if 'netherland' in countries:
                        key = VpnKey.objects.filter(user=user, server__country__name='netherland').last().key
                        await bot.send_message(call.message.chat.id, msg.key_avail)
                        await bot.send_message(call.message.chat.id, text=f'<code>{key}</code>',
                                               reply_markup=markup.key_menu(), parse_mode='HTML')
                    else:
                        await bot.send_message(call.message.chat.id, text=msg.no_key_avail,
                                               reply_markup=markup.get_subscription())
                elif 'poland' in data:
                    if 'poland' in countries:
                        key = VpnKey.objects.filter(user=user, server__country__name='poland').last().key
                        await bot.send_message(call.message.chat.id, msg.key_avail)
                        await bot.send_message(call.message.chat.id, text=f'<code>{key}</code>',
                                               reply_markup=markup.key_menu(), parse_mode='HTML')
                    else:
                        await bot.send_message(call.message.chat.id, text=msg.no_key_avail,
                                               reply_markup=markup.get_subscription())
                elif 'kazakhstan' in data:
                    if 'kazakhstan' in countries:
                        key = VpnKey.objects.filter(user=user, server__country__name='kazakhstan').last().key
                        await bot.send_message(call.message.chat.id, msg.key_avail)
                        await bot.send_message(call.message.chat.id, text=f'<code>{key}</code>',
                                               reply_markup=markup.key_menu(), parse_mode='HTML')
                    else:
                        await bot.send_message(call.message.chat.id, text=msg.no_key_avail,
                                               reply_markup=markup.get_subscription())
                elif 'russia' in data:
                    if 'russia' in countries:
                        key = VpnKey.objects.filter(user=user, server__country__name='russia').last().key
                        await bot.send_message(call.message.chat.id, msg.key_avail)
                        await bot.send_message(call.message.chat.id, text=f'<code>{key}</code>',
                                               reply_markup=markup.key_menu(), parse_mode='HTML')
                    else:
                        await bot.send_message(call.message.chat.id, text=msg.no_key_avail,
                                               reply_markup=markup.get_subscription())
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
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.send_message(call.message.chat.id, text=msg.help_message, reply_markup=markup.start(), parse_mode='HTML')
        elif 'popup_help' in data:
            await bot.answer_callback_query(call.id, text=msg.popup_help, show_alert=True)
        elif 'common_info' in data:
            ...
        elif 'back' in data:
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.send_message(chat_id=call.message.chat.id, text=msg.main_menu_choice, reply_markup=markup.start())


asyncio.run(bot.polling(non_stop=True))
