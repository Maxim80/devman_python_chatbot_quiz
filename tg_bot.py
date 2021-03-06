from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    RegexHandler
)
from telegram import ReplyKeyboardMarkup
from questions import get_questions
from exceptions import NoMoreQuestions
from functools import partial
from config import (
    TELEGRAM_TOKEN,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSW,
)
import redis
import logging
import json
import os
import enum
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class DialogStatus(enum.Enum):
    USER_CHOICE = 0


def start(bot, update, db):
    reply_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    markup = ReplyKeyboardMarkup(reply_keyboard)

    user_id = update.message.chat_id
    user_data = {'question': None, 'counter': 0}
    db.set(user_id, json.dumps(user_data))

    update.message.reply_text(
        'Привет! Я бот для викторины.',
        reply_markup=markup,
    )
    return DialogStatus.USER_CHOICE


def handle_new_question_request(bot, update, questions, db):
    user_id = update.message.chat_id
    user_data = json.loads(db.get(user_id))
    try:
        user_question = questions.get_question()
    except NoMoreQuestions:
        message = 'Конец викторины. Вы ответили на все вопросы.'
    else:
        message = user_question
        user_data['question'] = user_question
        db.set(user_id, json.dumps(user_data))

    update.message.reply_text(user_question)
    return DialogStatus.USER_CHOICE


def handle_solution_attempt(bot, update, questions, db):
    user_id = update.message.chat_id
    user_answer = update.message.text

    user_data = json.loads(db.get(user_id))
    user_question = user_data['question']

    is_user_answer_correctly = questions.check_answer(user_question,
        user_answer)

    if is_user_answer_correctly:
        message = 'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"'
        user_data['counter'] += 1
        db.set(user_id, json.dumps(user_data))
    else:
        message = 'Неправильно… Попробуешь ещё раз?'
    update.message.reply_text(message)
    return DialogStatus.USER_CHOICE


def handle_surrender_request(bot, update, questions, db):
    user_id = update.message.chat_id
    user_data = json.loads(db.get(user_id))
    user_question = user_data['question']
    answer = questions.delete_question(user_question)
    update.message.reply_text(answer)
    handle_new_question_request(bot, update, questions, db)


def handle_counter_request(bot, update, db):
    user_id = update.message.chat_id
    user_data = json.loads(db.get(user_id))
    counter = user_data['counter']
    update.message.reply_text(counter)
    return DialogStatus.USER_CHOICE


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    questions = get_questions()

    redis_db = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSW,
        db=0,
    )

    start_quiz = partial(start, db=redis_db)
    new_question = partial(handle_new_question_request, questions = questions, db=redis_db)
    solution_attempt = partial(handle_solution_attempt, questions=questions, db=redis_db)
    surrender = partial(handle_surrender_request, questions=questions, db=redis_db)
    counter = partial(handle_counter_request, db=redis_db)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_quiz)],

        states={
            DialogStatus.USER_CHOICE: [
                RegexHandler('^Новый вопрос$', new_question),
                RegexHandler('^Мой счет$', counter),
                RegexHandler('^Сдаться$', surrender),
                MessageHandler(Filters.text, solution_attempt),
            ],
        },
        fallbacks=[ConversationHandler.END]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
