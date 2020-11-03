import telebot

import logging
import os

from dotenv import load_dotenv


load_dotenv()
telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
telegram_token = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(telegram_token)

class MyLogsHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        bot.send_message(telegram_chat_id, log_entry)
