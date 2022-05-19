from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
from questions import upload_questions_and_answers, get_question
from functools import partial
import logging
import json
import redis
import os


QUESTIONS_AND_ANSWERS = upload_questions_and_answers()


def start(bot, update, db):
    """Send a message when the command /start is issued."""
    reply_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text(
        'Привет! Я бот для викторины.',
        reply_markup=markup,
    )
    questions_and_answers = upload_questions_and_answers()
    db.set('questions_and_answers', json.dumps(questions_and_answers))


def echo(bot, update, db):
    """Echo the user message."""
    user_id = update.message.chat_id
    user_choice = update.message.text
    questions_and_answers = json.loads(db.get('questions_and_answers'))
    if user_choice == 'Новый вопрос':
        question = get_question(questions_and_answers)
        update.message.reply_text(question)
        db.set(user_id, question)


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
    new_question = partial(echo, db=redis_db)
    dp.add_handler(CommandHandler("start", start_quiz))
    dp.add_handler(MessageHandler(Filters.text, new_question))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
