import asyncio
import logging
import traceback
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from math import ceil
from datetime import datetime, timedelta, date

from django.conf import settings
from telebot.async_telebot import AsyncTeleBot
from telebot.types import LabeledPrice

import django_orm
from bot.models import TelegramBot
from bot.models import TelegramUser
from bot.models import TelegramReferral
from bot.models import VpnKey
from bot.models import Server
from bot.models import Country
from bot.models import IncomeInfo
from bot.models import ReferralSettings
from bot.models import Logging

from bot.main import msg
from bot.main import markup
from bot.main.utils import return_matches
from bot.main.outline_client import create_new_key
from bot.main.outline_client import delete_user_keys
from bot.main.outline_client import update_keys_data_limit

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname) -8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y.%m.%d %I:%M:%S',
    handlers=[
        TimedRotatingFileHandler(filename='log/bot_log.log', when='D', interval=1, backupCount=5),
        logging.StreamHandler(stream=sys.stderr)
              ],
)

bot = AsyncTeleBot(TelegramBot.objects.get(pk=1).token)
bot.parse_mode = 'HTML'
DEBUG = settings.DEBUG


def update_sub_status(user: TelegramUser):
    exp_date = user.subscription_expiration
    if exp_date < datetime.now().date():
        TelegramUser.objects.filter(user_id=user.user_id).update(subscription_status=False)
    else:
        TelegramUser.objects.filter(user_id=user.user_id).update(subscription_status=True)


@bot.message_handler(commands=['test'])
async def start(message):
    logger.info(f'{message.from_user.id}: {message.text}')


@bot.message_handler(commands=['start'])
async def start(message):
    if message.chat.type == 'private':
        logger.info(f'[{message.from_user.first_name}:{message.from_user.username}:{message.from_user.id}] [msg: {message.text}]')
        try:
            TelegramUser.objects.create(user_id=message.from_user.id,
                                        username=message.from_user.username,
                                        first_name=message.from_user.first_name,
                                        last_name=message.from_user.last_name,
                                        data_limit=5368709120,  # 5 GB at start
                                        subscription_status=True,
                                        subscription_expiration=datetime.now() + timedelta(days=3))
            await bot.send_message(chat_id=message.chat.id, text=msg.new_user_bonus)
        except:
            ...
        await bot.send_message(chat_id=message.chat.id, text=msg.start_message.format(message.from_user.first_name))
        await bot.send_message(chat_id=message.chat.id, text=msg.main_menu_choice, reply_markup=markup.start())


@bot.message_handler(content_types=['text'])
async def handle_referral(message):
    if message.chat.type == 'private':
        logger.info(f'[{message.from_user.first_name}:{message.from_user.username}:{message.from_user.id}] [msg: {message.text}]')
        update_sub_status(user=TelegramUser.objects.get(user_id=message.chat.id))
        if 'start=' in message.text:
            referred_by = message.text.split('=')[-1]
            same_user_check = str(referred_by) == str(message.chat.id)
            if not same_user_check:
                try:
                    await bot.send_message(message.chat.id, text=f"Вы были приглашены пользователем с ID: {referred_by}")

                    referrer = TelegramUser.objects.get(user_id=referred_by)  # тот, от кого получена ссылка
                    referred = TelegramUser.objects.get(user_id=message.chat.id)  # тот, кто воспользовался ссылкой

                    TelegramReferral.objects.create(referrer=referrer, referred=referred, level=1)

                    await bot.send_message(chat_id=message.chat.id,
                                           text=msg.referral_bond.format(str(referrer.user_id), str(referred.user_id)))

                    #  Проверяем есть ли рефералы у того, кто отправил ссылку и получаем их список, если есть
                    referred_list = [x for x in TelegramReferral.objects.filter(referred=referrer, level__lte=4)]
                    for r in referred_list:
                        current_level = r.level  # 1
                        current_referrer = r.referrer
                        new_referral = TelegramReferral.objects.create(referrer=current_referrer, referred=referred,
                                                                       level=current_level + 1)
                        logger.info(f'Создана новая реферальная связь {new_referral}')
                    await bot.send_message(chat_id=message.chat.id,
                                           text=msg.start_message.format(message.from_user.first_name))
                    await bot.send_message(chat_id=message.chat.id, text=msg.main_menu)
                    await bot.send_message(chat_id=message.chat.id, text=msg.main_menu_choice,
                                           reply_markup=markup.start())
                except:
                    logger.error(f'{traceback.format_exc()}')

            else:
                await bot.send_message(chat_id=message.chat.id, text=msg.referral_bond_error)
                await bot.send_message(chat_id=message.chat.id,
                                       text=msg.start_message.format(message.from_user.first_name))
                await bot.send_message(chat_id=message.chat.id, text=msg.main_menu)
                await bot.send_message(chat_id=message.chat.id, text=msg.main_menu_choice, reply_markup=markup.start())
        else:
            user = TelegramUser.objects.get(user_id=message.chat.id)
            if user.top_up_balance_listener:

                try:
                    amount = int(message.text)
                    if amount >= 150:
                        await bot.send_message(chat_id=message.chat.id, text=msg.start_payment.format(str(amount)),
                                               reply_markup=markup.payment_ukassa(price=amount,
                                                                                  chat_id=message.chat.id))
                        TelegramUser.objects.filter(user_id=message.chat.id).update(top_up_balance_listener=False)
                    else:
                        await bot.send_message(chat_id=message.chat.id,
                                               text=msg.start_payment_error.format(message.text),
                                               reply_markup=markup.back())
                except:
                    await bot.send_message(chat_id=message.chat.id, text=msg.start_payment_error.format(message.text),
                                           reply_markup=markup.back())
                    logger.error(f'{traceback.format_exc()}')


@bot.pre_checkout_query_handler(func=lambda query: True)
async def checkout(pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True, error_message=msg.payment_unsuccessful)


@bot.message_handler(content_types=['successful_payment'])
async def got_payment(message):
    payment = message.successful_payment
    logger.info(f'[{message.from_user.first_name}:{message.from_user.username}:{message.from_user.id}] '
                f'[successful payment: {str(int(payment.total_amount)/100)} {payment.currency} | {payment}]')

    user = TelegramUser.objects.get(user_id=message.chat.id)
    amount = float(message.successful_payment.total_amount / 100)
    currency = message.successful_payment.currency
    await bot.send_message(chat_id=message.chat.id, text=msg.payment_successful.format(amount, currency))
    await bot.send_message(chat_id=message.chat.id, text=msg.main_menu_choice, reply_markup=markup.start())
    balance = float(TelegramUser.objects.get(user_id=message.chat.id).balance) + amount
    TelegramUser.objects.filter(user_id=message.chat.id).update(balance=balance)

    income = float(IncomeInfo.objects.get(pk=1).total_amount)  # Общий доход проекта
    users_balance = float(IncomeInfo.objects.get(pk=1).user_balance_total)  # Общий баланс всех пользователей
    IncomeInfo.objects.all().update(total_amount=income + amount, user_balance_total=users_balance + amount)

    referred_list = [x for x in TelegramReferral.objects.filter(referred=user)]
    if referred_list:
        for r in referred_list:
            user_to_pay = TelegramUser.objects.filter(user_id=r.referrer.user_id)[0]
            level = r.level
            percent = None
            if level == 1:
                percent = ReferralSettings.objects.get(pk=1).level_1_percentage
            elif level == 2:
                percent = ReferralSettings.objects.get(pk=1).level_2_percentage
            elif level == 3:
                percent = ReferralSettings.objects.get(pk=1).level_3_percentage
            elif level == 4:
                percent = ReferralSettings.objects.get(pk=1).level_4_percentage
            elif level == 5:
                percent = ReferralSettings.objects.get(pk=1).level_5_percentage
            if percent:
                income = float(TelegramUser.objects.get(user_id=user_to_pay.user_id).income) + (
                        amount * float(percent) / 100)
                TelegramUser.objects.filter(user_id=user_to_pay.user_id).update(income=income)
                await bot.send_message(user_to_pay.user_id,
                                       text=msg.income_from_referral.format(str(amount * float(percent) / 100)),
                                       reply_markup=markup.start())


@bot.callback_query_handler(func=lambda call: True)
async def callback_query_handlers(call):
    data = call.data.split(':')
    logger.info(f'[{call.message.chat.first_name}:{call.message.chat.username}:{call.message.chat.id}] [data: {call.data}]')
    user = TelegramUser.objects.get(user_id=call.message.chat.id)
    update_sub_status(user=user)
    country_list = [x.name for x in Country.objects.all()]

    async def send_dummy():
        await bot.send_message(call.message.chat.id, text=msg.dummy_message, reply_markup=markup.start())

    if call.message.chat.type == 'private':
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        if 'manage' in data:
            await bot.send_message(call.message.chat.id, msg.avail_location_choice,
                                   reply_markup=markup.get_avail_location())
        elif 'country' in data:
            if user.subscription_status:
                keys = VpnKey.objects.filter(user=user)
                country = return_matches(country_list, data)[0]

                if country:
                    try:
                        key = VpnKey.objects.filter(user=user, server__country__name=country).last().access_url
                        await bot.send_message(call.message.chat.id, text=f'{msg.key_avail}:\n<code>{key}</code>',
                                               reply_markup=markup.key_menu(country))
                    except:
                        logger.error(f'{traceback.format_exc()}')
                        await bot.send_message(call.message.chat.id, text=msg.get_new_key,
                                               reply_markup=markup.get_new_key(country))
            else:
                await bot.send_message(call.message.chat.id, msg.no_subscription,
                                       reply_markup=markup.get_subscription())

        elif 'account' in data:

            if 'get_new_key' in call.data:
                try:

                    #  Удаляем все предыдущие ключи
                    await delete_user_keys(user=user)
                    country = call.data.split('_')[-1]
                    key = await create_new_key(
                        server=Server.objects.filter(country__name=country, keys_generated__lte=100).last(), user=user)
                    await bot.send_message(call.message.chat.id, text=f'{msg.key_avail}:\n<code>{key}</code>',
                                           reply_markup=markup.key_menu(country))
                except:
                    logger.error(f'{traceback.format_exc()}')

            elif 'swap_key' in call.data:
                try:
                    #  Удаляем все предыдущие ключи
                    await delete_user_keys(user=user)

                    country = call.data.split('_')[-1]
                    key = await create_new_key(
                        server=Server.objects.filter(country__name=country, keys_generated__lte=100).last(), user=user)
                    await bot.send_message(call.message.chat.id, text=f'{msg.key_avail}:\n<code>{key}</code>',
                                           reply_markup=markup.key_menu(country))
                except:
                    logger.error(f'{traceback.format_exc()}')

            elif 'top_up_balance' in data:
                await bot.send_message(call.message.chat.id, text=msg.paymemt_menu, reply_markup=markup.paymemt_menu())

            elif 'buy_subscripton' in data:
                await bot.send_message(call.message.chat.id, text=msg.choose_subscription,
                                       reply_markup=markup.choose_subscription())

            elif 'payment' in data:
                if 'ukassa' in data:
                    await bot.send_message(call.message.chat.id, text=msg.top_up_balance)
                    TelegramUser.objects.filter(user_id=user.user_id).update(top_up_balance_listener=True)
                elif 'details' in data:
                    price = LabeledPrice(label='test', amount=int(data[-2]) * 100)
                    await bot.send_invoice(
                        chat_id=call.message.chat.id,
                        title='Outline VPN Key',
                        description='Пополнение баланса для генерации ключей Outline VPN',
                        invoice_payload=f'{str(user.user_id)}:{data[-2]}',
                        provider_token='381764678:TEST:82447',
                        currency='RUB',
                        prices=[price],
                        photo_url='https://bitlaunch.io/blog/content/images/size/w2000/2022/10/Outline-VPN.png',
                        photo_height=512,  # !=0/None or picture won't be shown
                        photo_width=512,
                        photo_size=512,
                        is_flexible=False,
                        # start_parameter=f'{str(hash(str(user.user_id*data[-2])))}',
                        start_parameter=f'some-string-may-be',
                        need_phone_number=True,
                    )

            elif 'sub' in data:
                user_balance = user.balance
                price = None
                days = None
                if data[-1] == '1':
                    price = 150
                    days = 31
                elif data[-1] == '2':
                    price = 400
                    days = 93
                elif data[-1] == '3':
                    price = 700
                    days = 186
                elif data[-1] == '4':
                    price = 1000
                    days = 366
                elif data[-1] == '5':
                    price = 2000
                    days = 9999
                if user_balance < price:
                    await bot.send_message(call.message.chat.id, text=msg.low_balance,
                                           reply_markup=markup.top_up_balance())
                else:
                    description = f' <code>{days}</code> за <code>{price}р.</code>'
                    await bot.send_message(call.message.chat.id, text=msg.confirm_subscription.format(description),
                                           reply_markup=markup.confirm_subscription(price=price, days=days))

            elif 'confirm_subscription' in data:
                user_balance = user.balance
                balance_after = user_balance - int(data[-2])
                days = int(data[-1])
                new_exp_date = user.subscription_expiration + timedelta(days=days)
                TelegramUser.objects.filter(user_id=user.user_id).update(
                    balance=balance_after, subscription_status=True,
                    subscription_expiration=new_exp_date)
                await bot.send_message(call.message.chat.id, text=msg.sub_successful.format(new_exp_date, data[-2]),
                                       reply_markup=markup.proceed_to_profile())

        # todo  Разобраться с остатками ГБ

        elif 'profile' in data:
            # try:
            #     await update_keys_data_limit(user=user)
            # except:
            #     print(traceback.format_exc())
            user_id = user.user_id
            balance = user.balance
            income = user.income
            sub = str(user.subscription_expiration) if user.subscription_status else 'Нет подписки'
            reg_date = str(user.join_date)
            data_limit = str(ceil(user.data_limit / (1016 ** 3)))

            await bot.send_message(call.message.chat.id,
                                   text=msg.profile.format(user_id, balance, sub, reg_date, income),
                                   reply_markup=markup.my_profile())

        elif 'referral' in data:
            bot_username = TelegramBot.objects.get(pk=1).username
            user_income = TelegramUser.objects.get(user_id=call.message.chat.id).income
            referral_code = call.message.chat.id
            inv_1_lvl = TelegramReferral.objects.filter(referrer=user, level=1).__len__()
            inv_2_lvl = TelegramReferral.objects.filter(referrer=user, level=2).__len__()
            inv_3_lvl = TelegramReferral.objects.filter(referrer=user, level=3).__len__()
            inv_4_lvl = TelegramReferral.objects.filter(referrer=user, level=4).__len__()
            inv_5_lvl = TelegramReferral.objects.filter(referrer=user, level=5).__len__()
            referral_link = f"Твоя реферальная ссылка: <code>https://t.me/{bot_username}?start={referral_code}</code>\n"
            await bot.send_message(call.message.chat.id,
                                   text=referral_link + msg.referral.format(inv_1_lvl, inv_2_lvl, inv_3_lvl, inv_4_lvl,
                                                                            inv_5_lvl, user_income),
                                   reply_markup=markup.withdraw_funds(call.message.chat.id))
        elif 'withdraw' in data:
            await bot.send_message(call.message.chat.id, text=msg.withdraw_request, reply_markup=markup.proceed_to_profile())

        elif 'help' in data:
            await bot.send_message(call.message.chat.id, text=msg.help_message, reply_markup=markup.start(),
                                   parse_mode='HTML')

        elif 'popup_help' in data:
            await bot.answer_callback_query(call.id, text=msg.popup_help, show_alert=True)

        elif 'common_info' in data:

            await bot.send_message(call.message.chat.id, text=msg.commom_info, reply_markup=markup.back())
        elif 'back' in data:
            await bot.send_message(chat_id=call.message.chat.id, text=msg.main_menu_choice, reply_markup=markup.start())

if __name__ == '__main__':
    asyncio.run(bot.polling(non_stop=True))
