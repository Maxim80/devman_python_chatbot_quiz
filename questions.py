import os
import random


QUESTIONS_DIRECTORY = os.path.join(os.getcwd(), 'questions_for_quiz')


def text_normalize(text):
    index = text.index(':')
    return text[index+1:].strip('\n')


def upload_questions_and_answers():
    questions = {}
    files = os.listdir(QUESTIONS_DIRECTORY)
    with open(os.path.join(QUESTIONS_DIRECTORY, files[0]), 'r', encoding='koi8-r') as f:
        text = f.read()

    text_lines = text.split('\n\n')

    for index, value in enumerate(text_lines):
        if 'Ответ:' in value:
            question = text_normalize(text_lines[index-1])
            answer = text_normalize(value)
            questions.update({question: answer})

    return questions


def get_question(questions):
    return random.choice(list(questions.keys()))


if __name__ == '__main__':
    questions = upload_questions_and_answers()
    question = get_question(questions)
    print(question)
