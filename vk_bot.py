from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from questions import Questions, NoMoreQuestions
import vk_api as vk
import random
import os
import redis
import json


def start(event, vk_api, keyboard, db):
    user_id = event.user_id
    user_data = {'question': None, 'counter': 0}
    db.set(user_id, json.dumps(user_data))
    message = 'Привет! Я бот для викторины.'

    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


def handle_new_question_request(event, vk_api, keyboard, questions, db):
    user_id = event.user_id
    user_data = json.loads(db.get(user_id))
    try:
        user_question = questions.get_question()
    except NoMoreQuestions:
        message = 'Конец викторины. Вы ответили на все вопросы.'
    else:
        message = user_question
        user_data['question'] = user_question
        db.set(user_id, json.dumps(user_data))

    vk_api.messages.send(
        user_id=user_id,
        message=message,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


def handle_solution_attempt(event, vk_api, keyboard, questions, db):
    user_id = event.user_id
    user_answer = event.text
    user_data = json.loads(db.get(user_id))
    user_question = user_data['question']
    is_user_answer_correct = questions.is_answer_correct(
        user_question,
        user_answer,
    )
    if is_user_answer_correct:
        message = 'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"'
        user_data['counter'] += 1
        db.set(user_id, json.dumps(user_data))
    else:
        message='Неправильно… Попробуешь ещё раз?'

    vk_api.messages.send(
        user_id=user_id,
        message=message,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


def handle_surrender_request(event, vk_api, keyboard, questions, db):
    user_id = event.user_id
    user_data = json.loads(db.get(user_id))
    user_question = user_data['question']
    answer = questions.get_correct_answer(user_question)
    vk_api.messages.send(
        user_id=user_id,
        message=answer,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )
    handle_new_question_request(event, vk_api, keyboard, questions, db)


def handle_counter_request(event, vk_api, keyboard, db):
    user_id = event.user_id
    user_data = json.loads(db.get(user_id))
    counter = user_data['counter']
    vk_api.messages.send(
        user_id=user_id,
        message=counter,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


def main():
    load_dotenv()
    vk_token = os.getenv('VK_TOKEN')
    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')
    redis_passw = os.getenv('REDIS_PASSW')

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.SECONDARY)

    redis_db = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_passw,
        db=0,
    )

    questions = Questions()

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text == 'start':
                    start(event, vk_api, keyboard, redis_db)
                elif event.text == 'Новый вопрос':
                    handle_new_question_request(
                        event, vk_api, keyboard, questions, redis_db)
                elif event.text == 'Сдаться':
                    handle_surrender_request(
                        event, vk_api, keyboard, questions, redis_db)
                elif event.text == 'Мой счет':
                    handle_counter_request(event, vk_api, keyboard, redis_db)
                else:
                    handle_solution_attempt(
                        event, vk_api, keyboard, questions, redis_db)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
