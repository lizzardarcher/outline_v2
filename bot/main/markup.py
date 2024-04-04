from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

# from bot.models import *


btn_back = InlineKeyboardButton(text=f'Назад', callback_data=f'back')


def start():
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text=f'Управление VPN', callback_data=f'manage')
    btn2 = InlineKeyboardButton(text=f'Профиль', callback_data=f'profile')
    btn3 = InlineKeyboardButton(text=f'Помощь', callback_data=f'help')
    btn4 = InlineKeyboardButton(text=f'Информация', callback_data=f'common_info')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
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
    markup.row(btn1, btn2)
    return markup
