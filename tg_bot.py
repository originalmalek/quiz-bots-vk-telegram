import logging
import os

import telebot
import redis as rdb

from dotenv import load_dotenv
from telegram_logger import MyLogsHandler
from get_questions import create_questions_and_answer_dict
from random import randint


telegram_access_token = os.getenv('TELEGRAM_TOKEN')
tg_bot = telebot.TeleBot(telegram_access_token)

logger = logging.getLogger('TG')


def send_message_tg(text, chat_id):
    tg_bot.send_message(chat_id, text)


def show_buttons(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    new_question_button = telebot.types.KeyboardButton('Новый вопрос ❓')
    get_answer_button = telebot.types.KeyboardButton('Сдаться 🤔')
    my_scores_button = telebot.types.KeyboardButton('Мой счет 📊')
    markup.row(new_question_button, get_answer_button)
    markup.row(my_scores_button)

    tg_bot.send_message(text='Нажми "Новый вопрос"', chat_id=chat_id, reply_markup=markup)


@tg_bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    redis.set(f'tg-{message.chat.id}', 0)
    send_message_tg('Это бот викторина. Играй бесплатно.', message.chat.id)
    show_buttons(message.chat.id)


@tg_bot.message_handler(regexp='новый вопрос')
def send_question(message):
    if int(redis.get(f'tg-{message.chat.id}')) > 0:
        send_message_tg('У вас есть не отвеченный вопрос. Для продолжения введите ответ или нажмите кнопку "Сдаться".',
                        message.chat.id)
        return None
    questions_id = randint(1, len(questions))
    redis.set(f'tg-{message.chat.id}', questions_id)
    send_message_tg(questions[questions_id]['question'], message.chat.id)


@tg_bot.message_handler(regexp='сдаться')
def send_answer(message):
    questions_id = int(redis.get(f'tg-{message.chat.id}'))
    if questions_id == 0:
        send_message_tg('У вас нет активного вопроса. Нажмите "Новый вопрос"', message.chat.id)
        return None
    redis.set(f'tg-{message.chat.id}', 0)
    answer = questions[questions_id]['answer']
    send_message_tg(f'Правильный ответ:\n{answer}', message.chat.id)


@tg_bot.message_handler(regexp='мой счет')
def send_scores(message):
    send_message_tg('Ваш счет: 777. Вы молодец!', message.chat.id)


@tg_bot.message_handler(content_types='text')
def check_answer(message):
    questions_id = int(redis.get(f'tg-{message.chat.id}'))
    if questions_id == 0:
        send_message_tg('У вас нет активного вопроса! Нажмите "Новый вопрос".', message.chat.id)
        return None
    answer = questions[questions_id]['answer'].split(sep='.')[0]
    if len(message.text) <= 3:
        send_message_tg('Ответ неверный, попробуйте еще раз.', message.chat.id)
        return None
    if message.text.lower() in answer.lower():
        redis.set(f'tg-{message.chat.id}', 0)
        send_message_tg(f'Вы угадали!\nТочный ответ: {answer}.\nДля следующего вопроса нажмите "Новый вопрос:"',
                        message.chat.id)
    else:
        send_message_tg(text='Ответ неверный, попробуйте еще раз.', chat_id=message.chat.id)


if __name__ == '__main__':
    load_dotenv()
    redis_host = os.getenv('REDIS_HOST')
    redis_pass = os.getenv('REDIS_PASS')
    redis_port = os.getenv('REDIS_PORT')
    logging.basicConfig(level=20)
    logger.addHandler(MyLogsHandler())

    redis = rdb.Redis(host=redis_host, password=redis_pass, port=redis_port)
    questions = create_questions_and_answer_dict()

    while True:
        try:
            logger.warning('Bot TG is working')
            tg_bot.polling(none_stop=True)
        except Exception as err:
            logger.error('Bot TG got an error')
            logger.error(err, exc_info=True)
