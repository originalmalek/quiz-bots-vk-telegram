import json
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


def show_buttons(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    new_question_button = telebot.types.KeyboardButton('Новый вопрос ❓')
    get_answer_button = telebot.types.KeyboardButton('Сдаться 🤔')
    my_scores_button = telebot.types.KeyboardButton('Мой счет 📊')
    markup.row(new_question_button, get_answer_button)
    markup.row(my_scores_button)

    tg_bot.send_message(text='Нажми "Новый вопрос"', chat_id=chat_id, reply_markup=markup)


def check_sent_question(message):
    question_answer = redis.get(f'tg-{message.chat.id}').decode(encoding='UTF-8')

    if question_answer == '0':
        tg_bot.send_message(message.chat.id, 'У вас нет активного вопроса. Нажмите "Новый вопрос"')
        return None
    return question_answer


@tg_bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    redis.set(f'tg-{message.chat.id}', 0)
    tg_bot.send_message(message.chat.id, 'Это бот викторина. Играй бесплатно.')
    show_buttons(message.chat.id)


@tg_bot.message_handler(regexp='новый вопрос')
def send_question(message):
    if redis.get(f'tg-{message.chat.id}').decode(encoding='UTF-8') != '0':
        tg_bot.send_message(message.chat.id,
                            'У вас есть не отвеченный вопрос. Для '
                            'продолжения введите ответ или нажмите кнопку "Сдаться".')
        return None
    questions_id = randint(1, len(questions))
    question = questions[questions_id]['question']
    answer = questions[questions_id]['answer'].split(sep='.')[0]

    redis.set(f'tg-{message.chat.id}', str({'question': question, 'answer': answer}))
    tg_bot.send_message(message.chat.id, question)


@tg_bot.message_handler(regexp='сдаться')
def send_answer(message):
    question_answer = check_sent_question(message)
    if not question_answer:
        return None

    answer = eval(question_answer)['answer']
    redis.set(f'tg-{message.chat.id}', 0)
    tg_bot.send_message(message.chat.id, f'Правильный ответ:\n{answer}')


@tg_bot.message_handler(regexp='мой счет')
def send_scores(message):
    tg_bot.send_message(message.chat.id, 'Ваш счет: 777. Вы молодец!')


@tg_bot.message_handler(content_types='text')
def check_answer(message):
    question_answer = check_sent_question(message)
    if not question_answer:
        return None

    answer = eval(question_answer)['answer']
    if len(message.text) < 3:
        tg_bot.send_message(message.chat.id, 'Ответ неверный, попробуйте еще раз.')
        return None

    if message.text.lower() in answer.lower():
        redis.set(f'tg-{message.chat.id}', 0)
        tg_bot.send_message(message.chat.id,
                            f'Вы угадали!\nТочный ответ: {answer}\nДля следующего вопроса нажмите "Новый вопрос:"')
    else:
        tg_bot.send_message(message.chat.id, 'Ответ неверный, попробуйте еще раз.')


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
            tg_bot.polling()
        except Exception as err:
            logger.error('Bot TG got an error')
            logger.error(err, exc_info=True)
            break
