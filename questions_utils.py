import os
import random


def text_normalize(text: str) -> str:
    """Выделяет из текста тело вопроса/ответа."""
    index = text.index(':')
    return text[index+1:].strip('\n')


def answer_normalize(answer: str) -> str:
    """
    Нормализует ответ пользователя, все что все что он ввел до точки или скобок.
    """
    index = answer.find('(')
    if index != -1:
        answer = answer[:index]

    index = answer.find('.')
    if index != -1:
        answer = answer[:index]

    answer = answer.lower().strip(' ."\'').replace(' -', '')
    return answer


def upload_questions() -> dict:
    """Загружает вопросы и ответы к ним из текстового файла в словарь."""
    questions_directory = os.path.join(os.getcwd(), 'questions_for_quiz')
    questions = {}
    files = os.listdir(questions_directory)
    with open(os.path.join(questions_directory, files[0]), 'r', encoding='koi8-r') as f:
        text = f.read()

    text_lines = text.split('\n\n')

    for index, value in enumerate(text_lines):
        if 'Ответ:' in value:
            question = text_normalize(text_lines[index-1])
            answer = text_normalize(value)
            questions.update({question: answer})

    return questions


def get_question(questions: dict) -> str:
    return random.choice(list(questions.keys()))


def user_answer_check(user_answer: str, correct_answer: str) -> bool:
    "Проверят ответ пользователя, сравнивая его с правильным ответом."
    user_answer = answer_normalize(user_answer)
    correct_answer = answer_normalize(correct_answer)
    if user_answer in correct_answer:
        return True
    else:
        return False
