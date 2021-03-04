# -*- coding: utf-8 -*-
import telebot
import aria2p
import os

Aria2_host=os.environ.get('Aria2_host')
Aria2_port="8080"
Aria2_secret=os.environ.get('Aria2_secret')

aria2 = aria2p.API(
    aria2p.Client(
        host=Aria2_host,
        port=int(Aria2_port),
        secret=Aria2_secret
    )
)


Telegram_bot_api=os.environ.get('Telegram_bot_api')
Telegram_user_id=os.environ.get('Telegram_user_id')
bot = telebot.TeleBot(Telegram_bot_api)
app_title=os.environ.get('Title')
BOT_name=bot.get_me().username