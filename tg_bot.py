from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
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
    NEW_QUESTION = 1
    USER_ANSWER = 2


def start(bot, update, db):
    """Send a message when the command /start is issued."""
    reply_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text(
        'Привет! Я бот для викторины.',
        reply_markup=markup,
    )
    questions = upload_questions()
    db.set('questions', json.dumps(questions))
    return DialogStatus.USER_CHOICE


def handle_new_question_request(bot, update, db):
    user_id = update.message.chat_id
    questions = json.loads(db.get('questions'))
    question_for_user = get_question(questions)
    update.message.reply_text(question_for_user)
    db.set(user_id, question_for_user)
    return DialogStatus.USER_ANSWER


def handle_solution_attempt(bot, update, db):
    user_id = update.message.chat_id
    user_answer = update.message.text
    questions = json.loads(db.get('questions'))
    question_for_user = db.get(user_id).decode('utf-8')
    correct_answer = questions[question_for_user]
    is_user_answer_correctly = user_answer_check(
        user_answer,
        correct_answer,
    )
    if is_user_answer_correctly:
        update.message.reply_text(
            'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос'
        )
        questions.pop(question_for_user)
        db.set('questions', json.dumps(questions))
        return DialogStatus.USER_CHOICE
    else:
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')
        return DialogStatus.USER_ANSWER


def handle_throw_in_towel(bot, update, db):
    user_id = update.message.chat_id
    questions = json.loads(db.get('questions'))
    user_question = db.get(user_id).decode()
    answer = questions[user_question]
    update.message.reply_text(answer)
    handle_new_question_request(bot, update, db)


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
    throw_in_towel = partial(handle_throw_in_towel, db=redis_db)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_quiz)],

        states={
            DialogStatus.USER_CHOICE: [
                RegexHandler('^Новый вопрос$', new_question),
                RegexHandler('^Мой счет$', new_question),
            ],
            DialogStatus.USER_ANSWER: [
                RegexHandler('^Сдаться$', throw_in_towel),
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
