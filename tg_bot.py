from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
import logging
import os


def text_formatting(text):
    index = text.index(':')
    return text[index+1:].strip('\n')


def get_questions(path_to_questions_directory):
    questions = {}
    files = os.listdir(path_to_questions_directory)
    with open(os.path.join(path_to_questions_directory, files[2]), 'r', encoding='koi8-r') as f:
        text = f.read()

    text_lines = text.split('\n\n')

    for index, value in enumerate(text_lines):
        if 'Ответ:' in value:
            question = text_formatting(text_lines[index-1])
            answer = text_formatting(value)
            questions.update({question: answer})

    return questions


def start(bot, update):
    """Send a message when the command /start is issued."""
    reply_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text('Привет! Я бот для викторины.', reply_markup=markup)


def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main():
    """Start the bot."""
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')

    path_to_questions_directory = os.path.join(os.getcwd(), 'questions_for_quiz')

    updater = Updater(telegram_token)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
