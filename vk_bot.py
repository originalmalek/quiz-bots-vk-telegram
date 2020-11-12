import json
import os
import logging

import redis as rdb
import vk_api

from dotenv import load_dotenv
from random import randint

from get_questions import create_questions_and_answer_dict
from telegram_logger import MyLogsHandler
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id


logger = logging.getLogger('VK quiz bot')


def send_message_vk(text, user_id):
    vk_api.messages.send(user_id=user_id, message=text, random_id=randint(1, 1000))


def send_question(user_id):
    if redis.get(f'vk-{user_id}').decode(encoding='UTF-8') != '0':
        send_message_vk('У вас есть не отвеченный вопрос. Для продолжения введите ответ или нажмите кнопку "Сдаться".',
                        user_id)
        return None
    questions_id = randint(1, len(questions))
    question = questions[questions_id]['question']
    answer = questions[questions_id]['answer'].split(sep='.')[0]
    redis.set(f'vk-{user_id}', json.dumps({'question': question, 'answer': answer}))
    send_message_vk(question, user_id)


def check_sent_question(user_id):
    question_answer = redis.get(f'vk-{user_id}').decode(encoding='UTF-8')
    if question_answer == '0':
        send_message_vk('У вас нет активного вопроса! Нажмите "Новый вопрос".', user_id)
        return None
    return question_answer


def send_answer(user_id):
    question_answer = check_sent_question(user_id)

    if not question_answer:
        return None

    answer = json.loads(question_answer)['answer']
    redis.set(f'vk-{user_id}', 0)
    send_message_vk(f'Правильный ответ:\n{answer}', user_id)


def send_scores(user_id):
    send_message_vk('Ваш счет: 777. Вы молодец!', user_id)


def show_keyboard(user_id):
    keyboard = VkKeyboard()

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()

    keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)

    vk_api.messages.send(peer_id=user_id, random_id=get_random_id(),
                         keyboard=keyboard.get_keyboard(), message='Нажмите "Новый вопрос".')


def check_answer(message_text, user_id):
    question_answer = check_sent_question(user_id)
    if not question_answer:
        return None
    answer = json.loads(question_answer)['answer']
    if len(message_text) < 3:
        send_message_vk(text='Ответ неверный, попробуйте еще раз.', user_id=user_id)
        return None
    if message_text.lower() in answer.lower():
        redis.set(f'vk-{user_id}', 0)
        send_message_vk(text=f'Вы угадали!\nТочный ответ: {answer}.\nДля следующего вопроса нажмите "Новый вопрос:"',
                        user_id=user_id)
    else:
        send_message_vk(text='Ответ неверный, попробуйте еще раз.', user_id=user_id)


def handle_user_request(message_text, user_id):
    if not redis.get(f'vk-{user_id}'):
        show_keyboard(user_id)

    if message_text.lower() == 'start':
        send_message_vk('Бот викторина. Играй бесплатно.', user_id)
        show_keyboard(user_id)
        return None

    if message_text.lower() == 'новый вопрос':
        send_question(user_id)
        return None

    if message_text.lower() == 'сдаться':
        send_answer(user_id)
        return None

    if message_text.lower() == 'мой счет':
        send_scores(user_id)
        return None

    check_answer(message_text, user_id)


if __name__ == '__main__':
    load_dotenv()
    redis_host = os.getenv('REDIS_HOST')
    redis_pass = os.getenv('REDIS_PASS')
    redis_port = os.getenv('REDIS_PORT')
    vk_token = os.getenv('VK_TOKEN')
    telegram_access_token = os.getenv('TELEGRAM_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

    redis = rdb.Redis(host=redis_host, password=redis_pass, port=redis_port)
    vk_session = vk_api.VkApi(token=vk_token)
    vk_api = vk_session.get_api()

    questions = create_questions_and_answer_dict()

    my_log_handler = MyLogsHandler(level=logging.DEBUG, telegram_token=telegram_access_token,
                                    chat_id=telegram_chat_id)
    logging.basicConfig(level=20)
    logger.addHandler(my_log_handler)

    while True:
        try:
            logger.warning('Bot VK is working')
            longpoll = VkLongPoll(vk_session)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    handle_user_request(event.text, event.user_id)
        except Exception as err:
            logger.error('Bot VK got an error')
            logger.error(err, exc_info=True)
