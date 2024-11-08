import traceback
import asyncio
from telebot import TeleBot
from telebot.async_telebot import AsyncTeleBot

from datetime import datetime, timedelta

import django_orm
from bot.models import TelegramBot
from bot.models import TelegramUser
from bot.models import TelegramReferral
from bot.models import VpnKey
from bot.models import Server
from bot.models import Country
from bot.models import IncomeInfo
from bot.models import ReferralSettings
from bot.models import WithdrawalRequest
from bot.models import Transaction
from bot.models import GlobalSettings
from bot.main.outline_client import create_new_key

bot = AsyncTeleBot(token=TelegramBot.objects.get(pk=1).token, parse_mode='HTML')

target_users = [x for x in TelegramUser.objects.filter(subscription_status=False, join_date__gte=datetime.now() - timedelta(days=7))]
# target_users = [x for x in TelegramUser.objects.filter(subscription_status=False)]
# target_users = [x for x in TelegramUser.objects.filter(user_id=6384819902)]

text = """
Привет! Я заметил что тебе не удалось очернить все преимущества нашего ВПН.

Напомню, VPN TON это:

🔥 быстрая скорость
🔥 надежность
🔥 серверы в Европе, США и России

✅ Для того чтоб это проверить, я продлеваю тебе доступ еще на 3⃣ дня!

✅ Вот новый <b>ключ</b> то сервера USA, просто нажми на него, чтобы <b>скопировать</b>

💎💎💎
<code>{0}</code>
💎💎💎

Чтобы им воспользоваться скачай приложение outline по нашим ссылкам и вставь туда ключ.

Жми старт /start для получения ссылок для скачивания.

Страну можно сменить в любое время!
"""


text_2 = """
⚡️Всем привет! Жаркое лето в самом разгаре и у меня хорошая новость для вас! 

⚡️Клиентов нашего сервиса становиться больше и теперь мы снижаем цены на все тарифы в 2! раза🔥

❗️Время действия предложения ограничено и если тебе понравился наш сервис VPN, успевай забрать выгоду 50% на любой тариф, оплатив его до конца месяца!
"""

text_3 = """
🎈 Привет! Рад сообщить что на сегодня можно полноценно пользоваться YouTube!

🎈 А если хочешь им пользоваться и тогда когда он станет не доступен в России - будем рады помочь!

🎈 Напомню, сейчас действует специальная цена на ВСЕ наши тарифы - от 149₽!

🎈 До конца августа предложение актуально!
"""

async def main():
    for user in target_users:
        try:
            key = await create_new_key(Server.objects.get(pk=2975076), user)
            TelegramUser.objects.filter(user_id=user.user_id).update(
                subscription_status=True,
                subscription_expiration=datetime.now() + timedelta(days=3)
            )
            await bot.send_message(chat_id=user.user_id, text=text.format(key))
            print(f'[Отправлено пользователю] [{user}] [{key}]')
        except Exception as e:
            print(f'[Не удалось отправить пользователю] [{user}] [{e}]')


async def main_2():
    for user in TelegramUser.objects.all():
        try:
            await bot.send_message(chat_id=user.user_id, text=text_2)
            print(f'[Отправлено пользователю] [{user}]')
        except Exception as e:
            print(f'[Не удалось отправить пользователю] [{user}] [{e}]')


async def main_3():
    counter_success = 0
    counter_fail = 0
    for user in TelegramUser.objects.filter(subscription_status=False):
        try:
            await bot.send_message(chat_id=user.user_id, text=text_2)
            counter_success += 1
            print(f'[Отправлено пользователю] [{user}]')
        except Exception as e:
            counter_fail += 1
            print(f'[Не удалось отправить пользователю] [{user}] [{e}]')
    print(f"[Отправлено - {counter_success}] [Не отправлено - {counter_fail}]")

if __name__ == '__main__':
    # for user in target_users:
    #     print(user.user_id, user.username, )
    asyncio.run(main_3())
