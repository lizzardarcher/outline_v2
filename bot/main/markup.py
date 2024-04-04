from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

from apps.bot.models import *

def choose_mode():
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(InlineKeyboardButton(text=f'Photo', callback_data=f'mode:photo'))
    markup.add(InlineKeyboardButton(text=f'Sticker', callback_data=f'mode:sticker'))
    return markup