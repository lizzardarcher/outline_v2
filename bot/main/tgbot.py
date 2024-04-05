import asyncio
import logging
import traceback

from django.db import IntegrityError
from django.conf import settings
from telebot.async_telebot import AsyncTeleBot

import django_orm
from bot.models import TelegramBot
from bot.models import TelegramUser
from bot.models import TelegramReferral
from bot.models import VpnKey
from bot.models import Server
from bot.models import Country

from bot.main import msg
from bot.main import markup
from bot.main.utils import return_matches
from bot.main.outline_client import create_new_key
from bot.main.outline_client import delete_user_keys

bot = AsyncTeleBot(TelegramBot.objects.get(pk=1).token)
logging.basicConfig(level=logging.DEBUG)
DEBUG = settings.DEBUG


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


@bot.message_handler(func=lambda message: True)
async def handle_referral(message):
    if message.chat.type == 'private':
        if 'start=' in message.text:
            referred_by = message.text.split('=')[-1]
            same_user_check = str(referred_by) == str(message.chat.id)
            if not same_user_check:
                try:
                    await bot.send_message(message.chat.id, text=f"Вы были приглашены пользователем с ID: {referred_by}")

                    if DEBUG: print('В попытке создать реферала')

                    referrer = TelegramUser.objects.get(user_id=referred_by)  # тот, от кого получена ссылка
                    referred = TelegramUser.objects.get(user_id=message.chat.id)  # тот, кто воспользовался ссылкой

                    if DEBUG: print('Создаём реферала 1го уровня')
                    TelegramReferral.objects.create(referrer=referrer, referred=referred, level=1)
                    if DEBUG: print('Успешно создали реферала 1го уровня')

                    await bot.send_message(chat_id=message.chat.id, text=msg.referral_bond.format(str(referrer), str(referred)))

                    #  Проверяем есть ли рефералы у того, кто отправил ссылку и получаем их список, если есть
                    referred_list = [x for x in TelegramReferral.objects.filter(referred=referrer)]
                    if DEBUG: print('referred_list', referred_list)

                    for r in referred_list:
                        current_level = r.level  # 1
                        current_referrer = r.referrer
                        new_referral = TelegramReferral.objects.create(referrer=current_referrer, referred=referred, level=current_level+1)
                        if DEBUG: print('Создана новая реферальная связь', new_referral)
                    await bot.send_message(chat_id=message.chat.id, text=msg.start_message.format(message.from_user.first_name))
                    await bot.send_message(chat_id=message.chat.id, text=msg.main_menu)
                    await bot.send_message(chat_id=message.chat.id, text=msg.main_menu_choice, reply_markup=markup.start())
                except:
                    print(traceback.format_exc())
            else:
                await bot.send_message(chat_id=message.chat.id, text=msg.referral_bond_error)
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
                country = return_matches(country_list, data)[0]

                if country:
                    try:
                        key = VpnKey.objects.filter(user=user, server__country__name=country).last().access_url
                        await bot.send_message(call.message.chat.id, text=f'{msg.key_avail}:\n<code>{key}</code>', reply_markup=markup.key_menu(country), parse_mode='HTML')
                    except:
                        if DEBUG: print(traceback.format_exc())
                        await bot.send_message(call.message.chat.id, text=msg.get_new_key, reply_markup=markup.get_new_key('russia'))
            else:
                await bot.send_message(call.message.chat.id, msg.no_subscription, reply_markup=markup.get_subscription())

        elif 'account' in data:

            if 'get_new_key' in call.data:
                try:
                    #  Удаляем все предыдущие ключи
                    await delete_user_keys(user=user)
                    country = call.data.split('_')[-1]
                    key = await create_new_key(
                        server=Server.objects.filter(country__name=country, keys_generated__lte=100).last(), user=user)
                    await bot.send_message(call.message.chat.id, text=f'{msg.key_avail}:\n<code>{key}</code>', reply_markup=markup.key_menu(country), parse_mode='HTML')
                except:
                    await bot.send_message(call.message.chat.id, text=f'{traceback.format_exc()}')

            elif 'swap_key' in call.data:
                try:
                    #  Удаляем все предыдущие ключи
                    await delete_user_keys(user=user)
                    country = call.data.split('_')[-1]
                    key = await create_new_key(
                        server=Server.objects.filter(country__name=country, keys_generated__lte=100).last(), user=user)
                    await bot.send_message(call.message.chat.id, text=f'{msg.key_avail}:\n<code>{key}</code>', reply_markup=markup.key_menu(country), parse_mode='HTML')
                except:
                    await bot.send_message(call.message.chat.id, text=f'{traceback.format_exc()}')

            elif 'top_up_balance' in data:
                await bot.send_message(call.message.chat.id, text=msg.paymemt_menu, reply_markup=markup.paymemt_menu())
            elif 'buy_subscripton' in data:
                await bot.send_message(call.message.chat.id, text=msg.choose_subscription,
                                       reply_markup=markup.choose_subscription())

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
                                   reply_markup=markup.my_profile(), parse_mode='HTML')

        elif 'referral' in data:
            bot_username = TelegramBot.objects.get(pk=1).username
            referral_code = call.message.chat.id
            referral_link = f"Твоя реферальная ссылка: https://t.me/{bot_username}?start={referral_code}"
            await bot.send_message(call.message.chat.id, text=referral_link, reply_markup=markup.my_profile())

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
