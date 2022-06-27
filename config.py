from dotenv import load_dotenv
import os


load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
VK_TOKEN = os.getenv('VK_TOKEN')
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSW = os.getenv('REDIS_PASSW')

PATH_TO_QUESTIONS_FILES = os.path.join(os.getcwd(), 'questions')
