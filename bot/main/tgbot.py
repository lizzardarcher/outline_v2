import asyncio
import logging
import traceback

from telebot.async_telebot import AsyncTeleBot

import django_orm
from bot.models import TelegramBot
from bot.models import TelegramUser
from bot.models import VpnKey
from bot.models import Server
from bot.models import Country

from bot.main import msg
from bot.main import markup
from bot.main.utils import is_matches_in_list, return_matches
from bot.main.outline_client import create_new_key

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
    country_list = [x.name for x in Country.objects.all()]
    async def send_dummy():
        await bot.send_message(call.message.chat.id, text=msg.dummy_message, reply_markup=markup.start())

    print(data)
    if call.message.chat.type == 'private':
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        if 'manage' in data:
            await bot.send_message(call.message.chat.id, msg.avail_location_choice,
                                   reply_markup=markup.get_avail_location())
        elif 'country' in data:
            if user.subscription_status:
                keys = VpnKey.objects.filter(user=user)
                countries = [x.server.country.name for x in keys]
                country = return_matches(country_list, data)

                if country:
                    try:
                        key = VpnKey.objects.filter(user=user, server__country__name=country).last().access_url
                        await bot.send_message(call.message.chat.id, msg.key_avail)
                        await bot.send_message(call.message.chat.id, text=f'<code>{key}</code>', reply_markup=markup.key_menu(), parse_mode='HTML')
                    except:
                        await bot.send_message(call.message.chat.id, text=msg.get_new_key,
                                               reply_markup=markup.get_new_key('russia'))


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
                    try:
                        key = VpnKey.objects.filter(user=user, server__country__name='russia').last().access_url
                        await bot.send_message(call.message.chat.id, msg.key_avail)
                        await bot.send_message(call.message.chat.id, text=f'<code>{key}</code>', reply_markup=markup.key_menu(), parse_mode='HTML')
                    except:
                        await bot.send_message(call.message.chat.id, text=msg.get_new_key, reply_markup=markup.get_new_key('russia'))


                # else:
                #     await bot.send_message(call.message.chat.id, text=msg.no_key_avail, reply_markup=markup.get_subscription())
            else:
                await bot.send_message(call.message.chat.id, msg.no_subscription,
                                       reply_markup=markup.get_subscription())
        elif 'account' in data:


            if 'get_new_key' in call.data:
                try:
                    country = call.data.split('_')[-1]
                    key = await create_new_key(
                        server=Server.objects.filter(country__name=country, keys_generated__lte=100).last(), user=user)
                    await bot.send_message(call.message.chat.id, msg.key_avail)
                    await bot.send_message(call.message.chat.id, text=f'<code>{key}</code>', reply_markup=markup.key_menu(), parse_mode='HTML')
                except:
                    await bot.send_message(call.message.chat.id, text=f'{traceback.format_exc()}')


            elif 'top_up_balance' in data:
                await bot.send_message(call.message.chat.id, text=msg.paymemt_menu, reply_markup=markup.paymemt_menu())
            elif 'buy_subscripton' in data:
                await bot.send_message(call.message.chat.id, text=msg.choose_subscription,
                                       reply_markup=markup.choose_subscription())

            elif 'swap_key' in call.data:
                await send_dummy()

            elif 'payment_1' in data:
                await send_dummy()
            elif 'payment_2' in data:
                await send_dummy()

            elif 'sub_1' in data:
                await send_dummy()
            elif 'sub_2' in data:
                await send_dummy()
            elif 'sub_3' in data:
                await send_dummy()
            elif 'sub_4' in data:
                await send_dummy()
            elif 'sub_5' in data:
                await send_dummy()

        elif 'profile' in data:
            user_id = user.user_id
            balance = user.balance
            sub = str(user.subscription_expiration) if user.subscription_status else 'Нет подписки'
            reg_date = str(user.join_date)
            await bot.send_message(call.message.chat.id, text=msg.profile.format(user_id, balance, sub, reg_date),
                                   reply_markup=markup.start(), parse_mode='HTML')
        elif 'help' in data:
            await bot.send_message(call.message.chat.id, text=msg.help_message, reply_markup=markup.start(),
                                   parse_mode='HTML')
        elif 'popup_help' in data:
            await bot.answer_callback_query(call.id, text=msg.popup_help, show_alert=True)
        elif 'common_info' in data:

            await bot.send_message(call.message.chat.id, text=msg.commom_info, reply_markup=markup.back())
        elif 'back' in data:
            await bot.send_message(chat_id=call.message.chat.id, text=msg.main_menu_choice, reply_markup=markup.start())


asyncio.run(bot.polling(non_stop=True))
