from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from telebot.types import LabeledPrice
from telebot.types import ShippingOption

# from bot.models import *


btn_back = InlineKeyboardButton(text=f'🔙 Назад', callback_data=f'back')


def start():
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text=f'💡 Управление VPN', callback_data=f'manage')
    btn2 = InlineKeyboardButton(text=f'👨 Профиль', callback_data=f'profile')
    btn3 = InlineKeyboardButton(text=f'🆘 Помощь', callback_data=f'help')
    btn4 = InlineKeyboardButton(text=f'ℹ Информация', callback_data=f'common_info')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    return markup


def back():
    markup = InlineKeyboardMarkup()
    markup.add(btn_back)
    return markup


def get_avail_location():
    markup = InlineKeyboardMarkup()
    # markup.add(InlineKeyboardButton(text=f'Нидерланды 🇳🇱', callback_data=f'country:netherland'))
    # markup.add(InlineKeyboardButton(text=f'Польша 🇵🇱', callback_data=f'country:poland'))
    # markup.add(InlineKeyboardButton(text=f'Казахстан 🇰🇿', callback_data=f'country:kazakhstan'))
    markup.add(InlineKeyboardButton(text=f'Россия 🇷🇺', callback_data=f'country:russia'))
    markup.add(btn_back)
    return markup


def get_subscription():
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text=f'💳 Пополнить баланс', callback_data=f'account:top_up_balance')
    btn2 = InlineKeyboardButton(text=f'💲 Купить подписку', callback_data=f'account:buy_subscripton')
    btn3 = InlineKeyboardButton(text=f'🆘 Помощь', callback_data=f'popup_help')
    markup.row(btn1, btn2)
    markup.row(btn3)
    markup.row(btn_back)
    return markup


def top_up_balance():
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text=f'💳 Пополнить баланс', callback_data=f'account:top_up_balance')
    markup.row(btn1)
    markup.row(btn_back)
    return markup


def confirm_subscription(price: int, days: int):
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text=f'✅ Подтвердить приобретение подписки', callback_data=f'account:confirm_subscription:{str(price)}:{str(days)}')
    markup.row(btn1)
    markup.row(btn_back)
    return markup


def proceed_to_profile():
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text=f'👨 Профиль', callback_data=f'profile')
    markup.row(btn1)
    markup.row(btn_back)
    return markup


def my_profile():
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text=f'💳 Пополнить баланс', callback_data=f'account:top_up_balance')
    btn2 = InlineKeyboardButton(text=f'💲 Купить подписку', callback_data=f'account:buy_subscripton')
    btn3 = InlineKeyboardButton(text=f'🤝 Реферальная программа', callback_data=f'referral')
    markup.row(btn1, btn2)
    markup.row(btn3)
    markup.row(btn_back)
    return markup


def paymemt_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=f'Юкасса', callback_data=f'account:payment:ukassa'))
    markup.add(InlineKeyboardButton(text=f'USDT', callback_data=f'account:payment:usdt'))
    markup.add(btn_back)
    return markup


def choose_subscription():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=f'🟢 1 месяц (150 р)', callback_data=f'account:sub:1'))
    markup.add(InlineKeyboardButton(text=f'🟢 3 месяца (400 р)', callback_data=f'account:sub:2'))
    markup.add(InlineKeyboardButton(text=f'🟢 6 месяцев (700 р)', callback_data=f'account:sub:3'))
    markup.add(InlineKeyboardButton(text=f'🟢 1 год (1000 р)', callback_data=f'account:sub:4'))
    markup.add(InlineKeyboardButton(text=f'🟢 Пожизненная (2000 р)', callback_data=f'account:sub:5'))
    markup.add(btn_back)
    return markup


def key_menu(country: str):
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text=f'🔃 Заменить ключ', callback_data=f'account:swap_key_{country}')
    btn2 = InlineKeyboardButton(text=f'❔ Помощь', callback_data=f'help')
    markup.row(btn1, btn2)
    markup.row(btn_back)
    return markup


def get_new_key(country: str):
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text=f'🔑 Получить новый ключ', callback_data=f'account:get_new_key_{country}')
    markup.row(btn1)
    markup.row(btn_back)
    return markup


def payment_ukassa(price: int, chat_id: int):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text="💳 Оплатить", callback_data=f'account:payment:details:{str(price)}:{str(chat_id)}'))
    markup.add(btn_back)
    return markup


def withdraw_funds(chat_id: int):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="🤑 Вывести деньги", callback_data=f'withdraw:{str(chat_id)}'))
    markup.add(btn_back)
    return markup
