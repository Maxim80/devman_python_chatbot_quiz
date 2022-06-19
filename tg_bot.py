from dotenv import load_dotenv
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    RegexHandler
)
from telegram import ReplyKeyboardMarkup
from questions import upload_questions, get_question, user_answer_check
from functools import partial
import logging
import json
import redis
import os
import enum
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class DialogStatus(enum.Enum):
    USER_CHOICE = 0


def start(bot, update, db):
    reply_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    markup = ReplyKeyboardMarkup(reply_keyboard)

    all_questions = upload_questions()
    db.set('all_questions', json.dumps(all_questions))

    user_id = update.message.chat_id
    user_data = {'question': None, 'counter': 0}
    db.set(user_id, json.dumps(user_data))

    update.message.reply_text(
        'Привет! Я бот для викторины.',
        reply_markup=markup,
    )
    return DialogStatus.USER_CHOICE


def handle_new_question_request(bot, update, db):
    user_id = update.message.chat_id
    all_questions = json.loads(db.get('all_questions'))
    user_data = json.loads(db.get(user_id))
    user_question = get_question(all_questions)
    update.message.reply_text(user_question)
    user_data['question'] = user_question
    db.set(user_id, json.dumps(user_data))
    return DialogStatus.USER_CHOICE


def handle_solution_attempt(bot, update, db):
    user_id = update.message.chat_id
    user_answer = update.message.text
    all_questions = json.loads(db.get('all_questions'))
    user_data = json.loads(db.get(user_id))
    user_question = user_data['question']
    correct_answer = all_questions[user_question]
    is_user_answer_correctly = user_answer_check(
        user_answer,
        correct_answer,
    )
    if is_user_answer_correctly:
        update.message.reply_text(
            'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос'
        )
        all_questions.pop(user_question)
        user_data['counter'] += 1
        db.set('all_questions', json.dumps(all_questions))
        db.set(user_id, json.dumps(user_data))
        return DialogStatus.USER_CHOICE
    else:
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')
        return DialogStatus.USER_CHOICE


def handle_surrender_request(bot, update, db):
    user_id = update.message.chat_id
    all_questions = json.loads(db.get('all_questions'))
    user_data = json.loads(db.get(user_id))
    user_question = user_data['question']
    answer = all_questions[user_question]
    update.message.reply_text(answer)
    handle_new_question_request(bot, update, db)


def handle_counter_request(bot, update, db):
    user_id = update.message.chat_id
    user_data = json.loads(db.get(user_id))
    counter = user_data['counter']
    update.message.reply_text(counter)
    return DialogStatus.USER_CHOICE


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')
    redis_passw = os.getenv('REDIS_PASSW')

    redis_db = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_passw,
        db=0,
    )

    updater = Updater(telegram_token)
    dp = updater.dispatcher

    start_quiz = partial(start, db=redis_db)
    new_question = partial(handle_new_question_request, db=redis_db)
    solution_attempt = partial(handle_solution_attempt, db=redis_db)
    surrender = partial(handle_surrender_request, db=redis_db)
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
