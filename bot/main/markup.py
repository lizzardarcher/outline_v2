from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

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
    btn1 = InlineKeyboardButton(text=f'Нидерланды 🇳🇱', callback_data=f'country:netherland')
    btn2 = InlineKeyboardButton(text=f'Польша 🇵🇱', callback_data=f'country:poland')
    btn3 = InlineKeyboardButton(text=f'Казахстан 🇰🇿', callback_data=f'country:kazakhstan')
    btn4 = InlineKeyboardButton(text=f'Россия 🇷🇺', callback_data=f'country:russia')
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    markup.row(btn_back)
    return markup


def get_subscription():
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text=f'Пополнить баланс', callback_data=f'account:top_up_balance')
    btn2 = InlineKeyboardButton(text=f'Купить подписку', callback_data=f'account:buy_subscripton')
    btn3 = InlineKeyboardButton(text=f'Помощь', callback_data=f'popup_help')
    markup.row(btn1, btn2)
    markup.row(btn3)
    markup.row(btn_back)
    return markup


def paymemt_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=f'Способ 1', callback_data=f'account:payment_1'))
    markup.add(InlineKeyboardButton(text=f'Способ 2 ', callback_data=f'account:payment_2'))
    markup.add(btn_back)
    return markup


def choose_subscription():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=f'1 месяц', callback_data=f'account:sub_1'))
    markup.add(InlineKeyboardButton(text=f'3 месяца', callback_data=f'account:sub_2'))
    markup.add(InlineKeyboardButton(text=f'6 месяцев', callback_data=f'account:sub_3'))
    markup.add(InlineKeyboardButton(text=f'1 год', callback_data=f'account:sub_4'))
    markup.add(InlineKeyboardButton(text=f'Пожизненная', callback_data=f'account:sub_5'))
    markup.add(btn_back)
    return markup


def key_menu():
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text=f'Заменить ключ', callback_data=f'account:swap_key')
    btn2 = InlineKeyboardButton(text=f'Помощь', callback_data=f'help')
    markup.row(btn1, btn2)
    markup.row(btn_back)
    return markup
