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


if __name__ == '__main__':
    # for user in target_users:
    #     print(user.user_id, user.username, )
    asyncio.run(main())
